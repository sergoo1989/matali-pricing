"""
محرك التسعير الذكي المبني على البيانات
Data-Driven Smart Pricing Engine

يحلل بيانات P&L لتوليد أسعار ذكية بناءً على:
- التكاليف التاريخية
- هوامش الربح
- ربحية العملاء
- حجم الطلبات
"""

import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st


class SmartPricingEngine:
    """محرك التسعير الذكي الأساسي"""
    
    def __init__(self, pnl_data):
        """
        تهيئة محرك التسعير
        
        Parameters:
        -----------
        pnl_data : pd.DataFrame
            بيانات P&L (الأرباح والخسائر)
        """
        self.data = pnl_data
        self.cost_analysis = self.analyze_costs()
        self.profit_margins = self.calculate_margins()
        self.service_stats = self.calculate_service_statistics()
    
    def analyze_costs(self):
        """تحليل التكاليف من بيانات P&L"""
        try:
            cost_breakdown = {}
            
            # تحليل تكاليف التجهيز
            processing_costs = self.data[
                self.data['Account Level 2'].str.contains('تجهيز', na=False, case=False)
            ]['net_amount'].values
            cost_breakdown['processing'] = abs(np.mean(processing_costs)) if len(processing_costs) > 0 else 50
            
            # تحليل تكاليف الشحن الداخلي
            shipping_local = self.data[
                self.data['Account Level 3'].str.contains('شحن داخل', na=False, case=False)
            ]['net_amount'].values
            cost_breakdown['shipping_local'] = abs(np.mean(shipping_local)) if len(shipping_local) > 0 else 30
            
            # تحليل تكاليف الشحن الخارجي
            shipping_external = self.data[
                self.data['Account Level 3'].str.contains('شحن خارج', na=False, case=False)
            ]['net_amount'].values
            cost_breakdown['shipping_external'] = abs(np.mean(shipping_external)) if len(shipping_external) > 0 else 100
            
            # تحليل تكاليف التخزين
            storage_costs = self.data[
                self.data['Account Level 2'].str.contains('تخزين', na=False, case=False)
            ]['net_amount'].values
            cost_breakdown['storage'] = abs(np.mean(storage_costs)) if len(storage_costs) > 0 else 20
            
            # تحليل التكاليف التشغيلية
            operational_costs = self.data[
                self.data['Account Level 2'].str.contains('عمومية|اداري', na=False, case=False)
            ]['net_amount'].values
            cost_breakdown['operational'] = abs(np.mean(operational_costs)) if len(operational_costs) > 0 else 100
            
            # تحليل تكاليف الاستلام
            receiving_costs = self.data[
                self.data['Account Level 2'].str.contains('استلام', na=False, case=False)
            ]['net_amount'].values
            cost_breakdown['receiving'] = abs(np.mean(receiving_costs)) if len(receiving_costs) > 0 else 15
            
            return cost_breakdown
            
        except Exception as e:
            st.warning(f"خطأ في تحليل التكاليف: {str(e)}")
            # قيم افتراضية
            return {
                'processing': 50,
                'shipping_local': 30,
                'shipping_external': 100,
                'storage': 20,
                'operational': 100,
                'receiving': 15
            }
    
    def calculate_margins(self):
        """حساب هوامش الربح التاريخية"""
        try:
            # حساب إجمالي الإيرادات
            total_income = abs(self.data[
                self.data['Account Level 1'].str.contains('income', na=False, case=False)
            ]['net_amount'].sum())
            
            # حساب إجمالي المصروفات
            total_expense = abs(self.data[
                self.data['Account Level 1'].str.contains('expense', na=False, case=False)
            ]['net_amount'].sum())
            
            # حساب هامش الربح
            if total_income > 0:
                avg_profit_margin = ((total_income - total_expense) / total_income) * 100
            else:
                avg_profit_margin = 20.0
            
            return {
                'historical_margin': max(0, avg_profit_margin),
                'total_income': total_income,
                'total_expense': total_expense,
                'net_profit': total_income - total_expense
            }
            
        except Exception as e:
            st.warning(f"خطأ في حساب الهوامش: {str(e)}")
            return {
                'historical_margin': 20.0,
                'total_income': 0,
                'total_expense': 0,
                'net_profit': 0
            }
    
    def calculate_service_statistics(self):
        """حساب إحصائيات الخدمات"""
        try:
            service_stats = {}
            
            # تحليل إيرادات التجهيز
            processing_income = self.data[
                self.data['Account Level 2'].str.contains('ايراد التجهيز|إيراد التجهيز', na=False, case=False)
            ]['net_amount'].values
            service_stats['processing'] = {
                'avg': abs(np.mean(processing_income)) if len(processing_income) > 0 else 150,
                'max': abs(np.max(processing_income)) if len(processing_income) > 0 else 300,
                'min': abs(np.min(processing_income)) if len(processing_income) > 0 else 50,
                'count': len(processing_income)
            }
            
            # تحليل إيرادات الشحن
            shipping_income = self.data[
                self.data['Account Level 2'].str.contains('ايراد الشحن|إيراد الشحن', na=False, case=False)
            ]['net_amount'].values
            service_stats['shipping'] = {
                'avg': abs(np.mean(shipping_income)) if len(shipping_income) > 0 else 200,
                'max': abs(np.max(shipping_income)) if len(shipping_income) > 0 else 400,
                'min': abs(np.min(shipping_income)) if len(shipping_income) > 0 else 100,
                'count': len(shipping_income)
            }
            
            # تحليل إيرادات التخزين
            storage_income = self.data[
                self.data['Account Level 2'].str.contains('ايراد التخزين|إيراد التخزين', na=False, case=False)
            ]['net_amount'].values
            service_stats['storage'] = {
                'avg': abs(np.mean(storage_income)) if len(storage_income) > 0 else 50,
                'max': abs(np.max(storage_income)) if len(storage_income) > 0 else 150,
                'min': abs(np.min(storage_income)) if len(storage_income) > 0 else 20,
                'count': len(storage_income)
            }
            
            # تحليل إيرادات الاستلام
            receiving_income = self.data[
                self.data['Account Level 2'].str.contains('ايراد الاستلام|إيراد الاستلام', na=False, case=False)
            ]['net_amount'].values
            service_stats['receiving'] = {
                'avg': abs(np.mean(receiving_income)) if len(receiving_income) > 0 else 30,
                'max': abs(np.max(receiving_income)) if len(receiving_income) > 0 else 80,
                'min': abs(np.min(receiving_income)) if len(receiving_income) > 0 else 10,
                'count': len(receiving_income)
            }
            
            return service_stats
            
        except Exception as e:
            st.warning(f"خطأ في حساب الإحصائيات: {str(e)}")
            return {
                'processing': {'avg': 150, 'max': 300, 'min': 50, 'count': 0},
                'shipping': {'avg': 200, 'max': 400, 'min': 100, 'count': 0},
                'storage': {'avg': 50, 'max': 150, 'min': 20, 'count': 0},
                'receiving': {'avg': 30, 'max': 80, 'min': 10, 'count': 0}
            }
    
    def calculate_price(self, service_type, cost_center, quantity=1, complexity=1.0):
        """
        حساب السعر بناءً على التكلفة والربحية
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة (ايراد التجهيز, ايراد الشحن, الخ)
        cost_center : str
            مركز التكلفة (متجر صفوة, الخ)
        quantity : int
            الكمية
        complexity : float
            معامل التعقيد (1.0 = عادي، أعلى = أكثر تعقيداً)
        
        Returns:
        --------
        dict
            تفاصيل السعر المحسوب
        """
        # الأسعار الأساسية من البيانات التاريخية
        base_prices = {
            'ايراد التجهيز': self.service_stats['processing']['avg'],
            'ايراد الشحن': self.service_stats['shipping']['avg'],
            'ايراد التخزين': self.service_stats['storage']['avg'],
            'ايراد الاستلام': self.service_stats['receiving']['avg']
        }
        
        # عوامل التكلفة لكل مركز تكلفة
        cost_center_multipliers = {
            'متجر صفوة': 1.0,
            'متجر بيست شيلد': 1.1,
            'متجر تكنو مارت': 0.9,
            'شركة تازيا': 1.2,
            'افتراضي': 1.0
        }
        
        # الحساب الأساسي
        base_price = base_prices.get(service_type, 100)
        cost_multiplier = cost_center_multipliers.get(cost_center, 1.0)
        
        # السعر قبل هامش الربح
        price_before_margin = base_price * cost_multiplier * complexity
        
        # إضافة هامش ربح مستهدف (20% كحد أدنى)
        target_margin = max(20, self.profit_margins['historical_margin'])
        final_price = price_before_margin * (1 + target_margin/100)
        
        # حساب السعر الإجمالي
        total_price = final_price * quantity
        
        return {
            'service_type': service_type,
            'cost_center': cost_center,
            'base_price': round(base_price, 2),
            'unit_price': round(final_price, 2),
            'quantity': quantity,
            'total_price': round(total_price, 2),
            'profit_margin': round(target_margin, 2),
            'complexity_factor': complexity,
            'cost_multiplier': cost_multiplier
        }


class AdvancedPricingEngine(SmartPricingEngine):
    """محرك التسعير المتقدم مع التحليلات الديناميكية"""
    
    def __init__(self, pnl_data):
        super().__init__(pnl_data)
        self.customer_profitability = self.analyze_customer_profitability()
    
    def analyze_customer_profitability(self):
        """تحليل ربحية كل عميل"""
        try:
            customer_data = {}
            
            # التأكد من وجود عمود Customer
            if 'Customer' not in self.data.columns:
                return customer_data
            
            for customer in self.data['Customer'].unique():
                if pd.notna(customer) and customer != '':
                    # حساب إيرادات العميل
                    customer_income = abs(self.data[
                        (self.data['Customer'] == customer) & 
                        (self.data['Account Level 1'].str.contains('income', na=False, case=False))
                    ]['net_amount'].sum())
                    
                    # حساب تكاليف العميل
                    customer_expenses = abs(self.data[
                        (self.data['Customer'] == customer) & 
                        (self.data['Account Level 1'].str.contains('expense', na=False, case=False))
                    ]['net_amount'].sum())
                    
                    # حساب الربحية
                    if customer_income > 0:
                        profitability = ((customer_income - customer_expenses) / customer_income) * 100
                        customer_data[customer] = {
                            'profitability': round(profitability, 2),
                            'income': round(customer_income, 2),
                            'expenses': round(customer_expenses, 2),
                            'net_profit': round(customer_income - customer_expenses, 2)
                        }
            
            return customer_data
            
        except Exception as e:
            st.warning(f"خطأ في تحليل ربحية العملاء: {str(e)}")
            return {}
    
    def dynamic_pricing(self, service_type, customer, volume, urgency='normal'):
        """
        تسعير ديناميكي بناءً على العميل وحجم الطلب
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        customer : str
            اسم العميل
        volume : int
            حجم الطلب
        urgency : str
            مستوى الأهمية (low, normal, high, urgent)
        
        Returns:
        --------
        dict
            تفاصيل السعر الديناميكي
        """
        # عوامل التسعير الديناميكي حسب الأهمية
        urgency_multipliers = {
            'low': 0.9,
            'normal': 1.0,
            'high': 1.3,
            'urgent': 1.5
        }
        
        # خصم حسب الحجم
        volume_discount = 1.0
        discount_applied = "لا يوجد"
        if volume > 1000:
            volume_discount = 0.85
            discount_applied = "15% (حجم كبير جداً)"
        elif volume > 500:
            volume_discount = 0.90
            discount_applied = "10% (حجم كبير)"
        elif volume > 100:
            volume_discount = 0.95
            discount_applied = "5% (حجم متوسط)"
        
        # تعديل حسب ربحية العميل
        customer_multiplier = 1.0
        customer_tier = "عادي"
        
        if customer in self.customer_profitability:
            customer_prof = self.customer_profitability[customer]['profitability']
            if customer_prof > 30:
                customer_multiplier = 0.85
                customer_tier = "VIP - خصم 15%"
            elif customer_prof > 20:
                customer_multiplier = 0.90
                customer_tier = "ممتاز - خصم 10%"
            elif customer_prof > 10:
                customer_multiplier = 0.95
                customer_tier = "جيد - خصم 5%"
            elif customer_prof < 0:
                customer_multiplier = 1.2
                customer_tier = "تحذير - زيادة 20%"
        
        # حساب السعر الأساسي
        base_calculation = self.calculate_price(service_type, customer, quantity=1)
        base_unit_price = base_calculation['unit_price']
        
        # حساب السعر الديناميكي
        dynamic_unit_price = (base_unit_price * 
                             urgency_multipliers[urgency] * 
                             volume_discount * 
                             customer_multiplier)
        
        total_price = dynamic_unit_price * volume
        
        return {
            'service_type': service_type,
            'customer': customer,
            'customer_tier': customer_tier,
            'base_unit_price': round(base_unit_price, 2),
            'dynamic_unit_price': round(dynamic_unit_price, 2),
            'volume': volume,
            'total_price': round(total_price, 2),
            'urgency': urgency,
            'urgency_multiplier': urgency_multipliers[urgency],
            'volume_discount': discount_applied,
            'savings': round((base_unit_price - dynamic_unit_price) * volume, 2)
        }
    
    def compare_pricing_strategies(self, service_type, quantity):
        """
        مقارنة استراتيجيات التسعير المختلفة
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        quantity : int
            الكمية
        
        Returns:
        --------
        dict
            مقارنة الأسعار لمختلف مراكز التكلفة
        """
        strategies = {}
        
        cost_centers = ['متجر صفوة', 'متجر بيست شيلد', 'متجر تكنو مارت', 'شركة تازيا']
        
        for center in cost_centers:
            price = self.calculate_price(
                service_type=service_type,
                cost_center=center,
                quantity=quantity
            )
            strategies[center] = price
        
        return strategies
    
    def get_pricing_recommendations(self, service_type, customer, volume):
        """
        الحصول على توصيات تسعير ذكية
        
        Parameters:
        -----------
        service_type : str
            نوع الخدمة
        customer : str
            العميل
        volume : int
            الحجم
        
        Returns:
        --------
        dict
            توصيات التسعير
        """
        recommendations = []
        
        # توصيات حسب الحجم
        if volume > 500:
            recommendations.append({
                'type': 'حجم',
                'message': f'حجم كبير ({volume} وحدة) - يُنصح بخصم {10 if volume > 1000 else 5}%',
                'priority': 'high'
            })
        
        # توصيات حسب العميل
        if customer in self.customer_profitability:
            prof = self.customer_profitability[customer]['profitability']
            if prof > 30:
                recommendations.append({
                    'type': 'عميل',
                    'message': f'عميل VIP (ربحية {prof:.1f}%) - قدم خصم خاص للحفاظ عليه',
                    'priority': 'high'
                })
            elif prof < 0:
                recommendations.append({
                    'type': 'تحذير',
                    'message': f'عميل غير مربح (خسارة {abs(prof):.1f}%) - راجع الأسعار',
                    'priority': 'critical'
                })
        
        # توصيات حسب نوع الخدمة
        service_stats = self.service_stats
        if service_type == 'ايراد الشحن' and volume > 100:
            recommendations.append({
                'type': 'خدمة',
                'message': 'خدمة شحن بحجم كبير - فكر في عقد شهري',
                'priority': 'medium'
            })
        
        return recommendations
