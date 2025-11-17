"""
معالج بيانات الموردين
Supplier Data Processor

يوفر:
- إدارة بيانات الموردين وشركات الشحن
- حساب تكاليف الخدمات الخارجية
- مقارنة الأسعار بين الموردين
- تحليل أفضل مورد لكل خدمة
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path


class SupplierDataProcessor:
    """معالج بيانات الموردين"""
    
    def __init__(self, suppliers_df=None):
        """
        تهيئة المعالج
        
        Parameters:
        -----------
        suppliers_df : pd.DataFrame
            بيانات الموردين
        """
        self.suppliers = suppliers_df
        
    def load_suppliers(self, file_path):
        """
        تحميل بيانات الموردين من ملف
        
        Parameters:
        -----------
        file_path : str
            مسار ملف الموردين
        
        Returns:
        --------
        pd.DataFrame
            بيانات الموردين
        """
        try:
            if str(file_path).endswith('.csv'):
                self.suppliers = pd.read_csv(file_path, encoding='utf-8-sig')
            else:
                self.suppliers = pd.read_excel(file_path)
            
            return self.suppliers
        except Exception as e:
            st.error(f"خطأ في تحميل بيانات الموردين: {str(e)}")
            return pd.DataFrame()
    
    def calculate_shipping_cost(self, city, weight, order_value, is_cod=False):
        """
        حساب تكلفة الشحن من الموردين
        
        Parameters:
        -----------
        city : str
            المدينة
        weight : float
            الوزن بالكيلو
        order_value : float
            قيمة الطلب
        is_cod : bool
            هل الدفع عند الاستلام
        
        Returns:
        --------
        dict
            تفاصيل تكلفة الشحن من كل مورد
        """
        if self.suppliers is None or len(self.suppliers) == 0:
            return {}
        
        shipping_suppliers = self.suppliers[
            self.suppliers['service_type'] == 'shipping'
        ].copy()
        
        if len(shipping_suppliers) == 0:
            return {}
        
        # تحديد إذا كانت المدينة داخل الرياض
        is_riyadh = 'رياض' in str(city).lower() if city else False
        
        results = {}
        
        for _, supplier in shipping_suppliers.iterrows():
            # اختيار السعر حسب الموقع
            base_price = supplier.get('price_inside_riyadh', 0) if is_riyadh else supplier.get('price_outside_riyadh', 0)
            
            # تخطي إذا السعر = 0 (المورد لا يخدم هذه المنطقة)
            if base_price == 0:
                continue
            
            # رسوم COD
            cod_fee = 0
            if is_cod:
                cod_fee = supplier.get('cod_fee', 0)
                # إذا كان COD نسبة من قيمة الطلب
                if cod_fee < 1:  # نسبة مئوية
                    cod_fee = order_value * cod_fee
            
            # رسوم الشبكة
            network_fee = supplier.get('network_fee', 0)
            
            # رسوم الوزن الإضافي
            weight_limit = supplier.get('weight_limit', 5.0)
            extra_kg_price = supplier.get('extra_kg_price', 0)
            
            weight_fee = 0
            if weight > weight_limit:
                extra_weight = weight - weight_limit
                weight_fee = extra_weight * extra_kg_price
            
            # الإجمالي
            total_cost = base_price + cod_fee + network_fee + weight_fee
            
            results[supplier['supplier_name']] = {
                'base_price': base_price,
                'cod_fee': cod_fee,
                'network_fee': network_fee,
                'weight_fee': weight_fee,
                'total_cost': total_cost,
                'service_type': 'shipping',
                'location': 'داخل الرياض' if is_riyadh else 'خارج الرياض'
            }
        
        return results
    
    def get_best_shipping_supplier(self, city, weight, order_value, is_cod=False):
        """
        الحصول على أفضل مورد شحن (أقل تكلفة)
        
        Parameters:
        -----------
        city : str
            المدينة
        weight : float
            الوزن
        order_value : float
            قيمة الطلب
        is_cod : bool
            COD
        
        Returns:
        --------
        dict
            أفضل مورد
        """
        all_costs = self.calculate_shipping_cost(city, weight, order_value, is_cod)
        
        if not all_costs:
            return None
        
        # ترتيب حسب التكلفة
        sorted_suppliers = sorted(all_costs.items(), key=lambda x: x[1]['total_cost'])
        
        best_supplier_name, best_details = sorted_suppliers[0]
        
        return {
            'supplier_name': best_supplier_name,
            **best_details
        }
    
    def calculate_fulfillment_cost(self, service_type='fulfillment'):
        """
        حساب تكلفة التجهيز من الموردين
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة (fulfillment, storage, VAS)
        
        Returns:
        --------
        dict
            تكاليف الخدمة من كل مورد
        """
        if self.suppliers is None or len(self.suppliers) == 0:
            return {}
        
        service_suppliers = self.suppliers[
            self.suppliers['service_type'] == service_type
        ].copy()
        
        results = {}
        
        for _, supplier in service_suppliers.iterrows():
            results[supplier['supplier_name']] = {
                'base_price': supplier.get('base_price', 0),
                'service_type': service_type,
                'can_provide_fulfillment': supplier.get('is_fulfillment_provider', 'no') == 'yes'
            }
        
        return results
    
    def get_outsourcing_options(self):
        """
        الحصول على موردين التجهيز الخارجي
        
        Returns:
        --------
        pd.DataFrame
            قائمة موردين التجهيز الخارجي
        """
        if self.suppliers is None or len(self.suppliers) == 0:
            return pd.DataFrame()
        
        return self.suppliers[
            self.suppliers['is_fulfillment_provider'] == 'yes'
        ].copy()
    
    def compare_suppliers(self, service_type, city=None, weight=5, order_value=100):
        """
        مقارنة جميع الموردين لخدمة معينة
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        city : str
            المدينة (للشحن)
        weight : float
            الوزن
        order_value : float
            قيمة الطلب
        
        Returns:
        --------
        pd.DataFrame
            مقارنة شاملة
        """
        if service_type == 'shipping':
            costs = self.calculate_shipping_cost(city, weight, order_value, is_cod=True)
            
            comparison = []
            for supplier_name, details in costs.items():
                comparison.append({
                    'المورد': supplier_name,
                    'السعر الأساسي': details['base_price'],
                    'رسوم COD': details['cod_fee'],
                    'رسوم الشبكة': details['network_fee'],
                    'رسوم الوزن': details['weight_fee'],
                    'الإجمالي': details['total_cost'],
                    'الموقع': details['location']
                })
            
            return pd.DataFrame(comparison).sort_values('الإجمالي')
        
        else:
            costs = self.calculate_fulfillment_cost(service_type)
            
            comparison = []
            for supplier_name, details in costs.items():
                comparison.append({
                    'المورد': supplier_name,
                    'السعر': details['base_price'],
                    'النوع': service_type
                })
            
            return pd.DataFrame(comparison).sort_values('السعر')
    
    def add_supplier(self, supplier_data):
        """
        إضافة مورد جديد
        
        Parameters:
        -----------
        supplier_data : dict
            بيانات المورد الجديد
        
        Returns:
        --------
        pd.DataFrame
            البيانات المحدثة
        """
        new_row = pd.DataFrame([supplier_data])
        
        if self.suppliers is None or len(self.suppliers) == 0:
            self.suppliers = new_row
        else:
            self.suppliers = pd.concat([self.suppliers, new_row], ignore_index=True)
        
        return self.suppliers
    
    def save_suppliers(self, file_path='data/suppliers.csv'):
        """
        حفظ بيانات الموردين
        
        Parameters:
        -----------
        file_path : str
            مسار الحفظ
        """
        if self.suppliers is not None:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            self.suppliers.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True
        return False
