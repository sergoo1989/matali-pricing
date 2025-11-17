"""
مدير قاعدة البيانات
Database Manager for Persistent Storage

يوفر:
- حفظ دائم لجميع البيانات
- قاعدة بيانات SQLite سريعة وآمنة
- استرجاع تلقائي عند بدء البرنامج
- إدارة جميع الجداول
"""

import sqlite3
import pandas as pd
import pickle
import json
from pathlib import Path
from datetime import datetime
import streamlit as st


class DatabaseManager:
    """مدير قاعدة البيانات للحفظ الدائم"""
    
    def __init__(self, db_path='data/matali_pricing.db'):
        """
        تهيئة قاعدة البيانات
        
        Parameters:
        -----------
        db_path : str
            مسار قاعدة البيانات
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # إنشاء الاتصال
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # إنشاء الجداول
        self.create_tables()
    
    def create_tables(self):
        """إنشاء جميع الجداول المطلوبة"""
        
        # جدول البيانات الرئيسية
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT UNIQUE NOT NULL,
                data_json TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                row_count INTEGER,
                column_count INTEGER
            )
        ''')
        
        # جدول الإعدادات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول العروض
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quote_id TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                service_type TEXT,
                total_price REAL,
                data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول سجل التغييرات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS changelog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT,
                action TEXT,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def save_dataframe(self, table_name, df):
        """
        حفظ DataFrame في قاعدة البيانات
        
        Parameters:
        -----------
        table_name : str
            اسم الجدول (capacity, pnl, orders, etc.)
        df : pd.DataFrame
            البيانات للحفظ
        
        Returns:
        --------
        bool
            نجاح العملية
        """
        try:
            # تحويل DataFrame إلى JSON
            data_json = df.to_json(orient='split', date_format='iso')
            
            # حفظ في قاعدة البيانات
            self.cursor.execute('''
                INSERT OR REPLACE INTO data_tables 
                (table_name, data_json, last_updated, row_count, column_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                table_name,
                data_json,
                datetime.now(),
                len(df),
                len(df.columns)
            ))
            
            # سجل التغيير
            self.cursor.execute('''
                INSERT INTO changelog (table_name, action, description)
                VALUES (?, ?, ?)
            ''', (table_name, 'SAVE', f'Saved {len(df)} rows'))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            st.error(f"خطأ في حفظ البيانات: {str(e)}")
            return False
    
    def load_dataframe(self, table_name):
        """
        تحميل DataFrame من قاعدة البيانات
        
        Parameters:
        -----------
        table_name : str
            اسم الجدول
        
        Returns:
        --------
        pd.DataFrame or None
            البيانات المحملة
        """
        try:
            self.cursor.execute('''
                SELECT data_json FROM data_tables WHERE table_name = ?
            ''', (table_name,))
            
            result = self.cursor.fetchone()
            
            if result:
                data_json = result[0]
                df = pd.read_json(data_json, orient='split')
                return df
            else:
                return None
                
        except Exception as e:
            st.warning(f"لم يتم العثور على بيانات {table_name}")
            return None
    
    def delete_table(self, table_name):
        """
        حذف جدول من قاعدة البيانات
        
        Parameters:
        -----------
        table_name : str
            اسم الجدول للحذف
        
        Returns:
        --------
        bool
            نجاح العملية
        """
        try:
            self.cursor.execute('''
                DELETE FROM data_tables WHERE table_name = ?
            ''', (table_name,))
            
            # سجل التغيير
            self.cursor.execute('''
                INSERT INTO changelog (table_name, action, description)
                VALUES (?, ?, ?)
            ''', (table_name, 'DELETE', 'Table deleted'))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            st.error(f"خطأ في حذف البيانات: {str(e)}")
            return False
    
    def get_all_tables(self):
        """
        الحصول على قائمة بجميع الجداول المحفوظة
        
        Returns:
        --------
        pd.DataFrame
            معلومات الجداول
        """
        try:
            query = '''
                SELECT 
                    table_name,
                    last_updated,
                    row_count,
                    column_count
                FROM data_tables
                ORDER BY last_updated DESC
            '''
            
            df = pd.read_sql_query(query, self.conn)
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def table_exists(self, table_name):
        """
        التحقق من وجود جدول
        
        Parameters:
        -----------
        table_name : str
            اسم الجدول
        
        Returns:
        --------
        bool
            هل الجدول موجود
        """
        self.cursor.execute('''
            SELECT COUNT(*) FROM data_tables WHERE table_name = ?
        ''', (table_name,))
        
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def save_quote(self, quote_data):
        """
        حفظ عرض سعر
        
        Parameters:
        -----------
        quote_data : dict
            بيانات العرض
        
        Returns:
        --------
        str
            معرف العرض
        """
        try:
            quote_id = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.cursor.execute('''
                INSERT INTO quotes 
                (quote_id, customer_name, service_type, total_price, data_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                quote_id,
                quote_data.get('customer', ''),
                quote_data.get('service_type', ''),
                quote_data.get('grand_total', 0),
                json.dumps(quote_data, ensure_ascii=False)
            ))
            
            self.conn.commit()
            return quote_id
            
        except Exception as e:
            st.error(f"خطأ في حفظ العرض: {str(e)}")
            return None
    
    def get_all_quotes(self):
        """
        الحصول على جميع العروض
        
        Returns:
        --------
        pd.DataFrame
            قائمة العروض
        """
        try:
            query = '''
                SELECT 
                    quote_id,
                    customer_name,
                    service_type,
                    total_price,
                    created_at,
                    data_json
                FROM quotes
                ORDER BY created_at DESC
            '''
            
            df = pd.read_sql_query(query, self.conn)
            
            # استخراج البيانات الإضافية من JSON
            if not df.empty and 'data_json' in df.columns:
                for idx, row in df.iterrows():
                    try:
                        quote_data = json.loads(row['data_json']) if pd.notna(row['data_json']) else {}
                        df.at[idx, 'monthly_volume'] = quote_data.get('monthly_volume')
                        df.at[idx, 'customer_tier'] = quote_data.get('customer_tier')
                        df.at[idx, 'pricing_model'] = quote_data.get('pricing_model')
                        df.at[idx, 'avg_order_value'] = quote_data.get('avg_order_value')
                        df.at[idx, 'profit_margin'] = quote_data.get('profit_margin')
                        df.at[idx, 'cost_breakdown'] = json.dumps(quote_data.get('cost_breakdown', {})) if 'cost_breakdown' in quote_data else None
                    except:
                        pass
            
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def delete_quote(self, quote_id):
        """
        حذف عرض سعر
        
        Parameters:
        -----------
        quote_id : str
            معرف العرض
        
        Returns:
        --------
        bool
            نجاح العملية
        """
        try:
            self.cursor.execute('DELETE FROM quotes WHERE quote_id = ?', (quote_id,))
            self.conn.commit()
            return True
        except Exception as e:
            st.error(f"خطأ في حذف العرض: {str(e)}")
            return False
    
    def save_setting(self, key, value):
        """حفظ إعداد"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, last_updated)
                VALUES (?, ?, ?)
            ''', (key, str(value), datetime.now()))
            
            self.conn.commit()
            return True
        except:
            return False
    
    def get_setting(self, key, default=None):
        """الحصول على إعداد"""
        try:
            self.cursor.execute('''
                SELECT value FROM settings WHERE key = ?
            ''', (key,))
            
            result = self.cursor.fetchone()
            return result[0] if result else default
        except:
            return default
    
    def get_changelog(self, limit=50):
        """
        الحصول على سجل التغييرات
        
        Parameters:
        -----------
        limit : int
            عدد السجلات
        
        Returns:
        --------
        pd.DataFrame
            سجل التغييرات
        """
        try:
            query = f'''
                SELECT 
                    table_name,
                    action,
                    description,
                    timestamp
                FROM changelog
                ORDER BY timestamp DESC
                LIMIT {limit}
            '''
            
            df = pd.read_sql_query(query, self.conn)
            return df
            
        except Exception as e:
            return pd.DataFrame()
    
    def clear_all_data(self):
        """
        حذف جميع البيانات (إعادة تعيين)
        
        Returns:
        --------
        bool
            نجاح العملية
        """
        try:
            self.cursor.execute('DELETE FROM data_tables')
            self.cursor.execute('DELETE FROM quotes')
            
            self.cursor.execute('''
                INSERT INTO changelog (table_name, action, description)
                VALUES (?, ?, ?)
            ''', ('ALL', 'CLEAR', 'All data cleared'))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            st.error(f"خطأ في حذف البيانات: {str(e)}")
            return False
    
    def export_backup(self, backup_path='data/backup.sql'):
        """
        تصدير نسخة احتياطية
        
        Parameters:
        -----------
        backup_path : str
            مسار النسخة الاحتياطية
        
        Returns:
        --------
        bool
            نجاح العملية
        """
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                for line in self.conn.iterdump():
                    f.write(f'{line}\n')
            
            return True
            
        except Exception as e:
            st.error(f"خطأ في التصدير: {str(e)}")
            return False
    
    def get_database_info(self):
        """
        الحصول على معلومات قاعدة البيانات
        
        Returns:
        --------
        dict
            معلومات قاعدة البيانات
        """
        try:
            # حجم قاعدة البيانات
            db_size = self.db_path.stat().st_size / 1024  # KB
            
            # عدد الجداول
            self.cursor.execute('SELECT COUNT(*) FROM data_tables')
            table_count = self.cursor.fetchone()[0]
            
            # عدد العروض
            self.cursor.execute('SELECT COUNT(*) FROM quotes')
            quote_count = self.cursor.fetchone()[0]
            
            # آخر تحديث
            self.cursor.execute('SELECT MAX(last_updated) FROM data_tables')
            last_update = self.cursor.fetchone()[0]
            
            return {
                'db_size_kb': round(db_size, 2),
                'table_count': table_count,
                'quote_count': quote_count,
                'last_update': last_update,
                'db_path': str(self.db_path)
            }
            
        except Exception as e:
            return {}
    
    def close(self):
        """إغلاق الاتصال"""
        try:
            self.conn.close()
        except:
            pass
    
    def __del__(self):
        """Destructor"""
        self.close()
