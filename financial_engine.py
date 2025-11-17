"""
المحرك المالي - طبقة الحسابات المالية المشتركة
Financial Engine - Shared Financial Calculations Layer

هذا الملف يحتوي على جميع الدوال المالية الأساسية التي تستخدمها جميع نماذج التسعير
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List


class FinancialEngine:
    """
    المحرك المالي الموحد لحسابات التسعير
    Unified Financial Engine for Pricing Calculations
    """
    
    def __init__(self):
        """تهيئة المحرك المالي"""
        self.pl_data = None
        self.capacity_data = None
        self.orders_data = None
        self.unit_costs = {}
        
    # =====================================================
    # 1️⃣ تحميل البيانات من المصادر المختلفة
    # =====================================================
    
    def load_pl_costs(self, pl_df: pd.DataFrame) -> Dict[str, float]:
        """
        استخراج التكاليف من بيانات P&L
        
        Returns:
        --------
        dict: {
            'fulfillment_cost_per_order': float,
            'storage_cost_per_pallet': float,
            'shipping_cost_per_order': float,
            'overhead_per_order': float,
            'total_monthly_expense': float,
            'order_count': int
        }
        """
        self.pl_data = pl_df
        costs = {}
        
        try:
            # استخراج التكاليف من Account Level 2
            fulfillment_expense = pl_df[pl_df['Account Level 2'].str.contains('تجهيز|Fulfillment', case=False, na=False)]['Amount'].sum()
            storage_expense = pl_df[pl_df['Account Level 2'].str.contains('تخزين|Storage|Warehouse', case=False, na=False)]['Amount'].sum()
            shipping_expense = pl_df[pl_df['Account Level 2'].str.contains('شحن|Shipping|Delivery', case=False, na=False)]['Amount'].sum()
            overhead_expense = pl_df[pl_df['Account Level 2'].str.contains('عمومية|إدارية|Overhead|Admin', case=False, na=False)]['Amount'].sum()
            
            # إجمالي المصروفات
            total_expense = abs(pl_df[pl_df['Amount'] < 0]['Amount'].sum())
            
            # عدد الطلبات (من بيانات الطلبات أو تقدير)
            order_count = 10000  # قيمة افتراضية، سيتم تحديثها من orders_data
            
            costs = {
                'fulfillment_total': abs(fulfillment_expense),
                'storage_total': abs(storage_expense),
                'shipping_total': abs(shipping_expense),
                'overhead_total': abs(overhead_expense),
                'total_monthly_expense': total_expense,
                'order_count': order_count,
                'fulfillment_cost_per_order': abs(fulfillment_expense) / order_count if order_count > 0 else 0,
                'storage_cost_per_order': abs(storage_expense) / order_count if order_count > 0 else 0,
                'shipping_cost_per_order': abs(shipping_expense) / order_count if order_count > 0 else 0,
                'overhead_cost_per_order': abs(overhead_expense) / order_count if order_count > 0 else 0,
            }
            
        except Exception as e:
            # قيم افتراضية في حالة عدم وجود بيانات
            costs = {
                'fulfillment_total': 0,
                'storage_total': 0,
                'shipping_total': 0,
                'overhead_total': 0,
                'total_monthly_expense': 0,
                'order_count': 0,
                'fulfillment_cost_per_order': 0,
                'storage_cost_per_order': 0,
                'shipping_cost_per_order': 0,
                'overhead_cost_per_order': 0,
            }
        
        return costs
    
    def load_capacity(self, capacity_df: pd.DataFrame) -> Dict[str, float]:
        """
        استخراج بيانات الطاقة الإنتاجية
        
        Returns:
        --------
        dict: {
            'max_fulfillment_capacity': float,  # طلب/شهر
            'max_storage_pallets': float,       # طبلية
            'max_receiving_pallets': float,      # طبلية/شهر
            'current_pallets_used': float,
            'available_pallets': float
        }
        """
        self.capacity_data = capacity_df
        capacity_info = {}
        
        try:
            # استخراج الطاقات القصوى
            fulfillment_row = capacity_df[capacity_df['Service'].str.contains('تجهيز|Fulfillment', case=False, na=False)]
            storage_row = capacity_df[capacity_df['Service'].str.contains('تخزين|Storage', case=False, na=False)]
            
            capacity_info = {
                'max_fulfillment_capacity': fulfillment_row['Monthly Capacity'].iloc[0] if not fulfillment_row.empty else 50000,
                'max_storage_pallets': storage_row['Storage Capacity (Pallets)'].iloc[0] if not storage_row.empty and 'Storage Capacity (Pallets)' in storage_row.columns else 468,
                'max_receiving_pallets': 1000,  # قيمة افتراضية
                'current_pallets_used': storage_row['Current Usage'].iloc[0] if not storage_row.empty and 'Current Usage' in storage_row.columns else 0,
            }
            
            capacity_info['available_pallets'] = capacity_info['max_storage_pallets'] - capacity_info['current_pallets_used']
            
        except Exception as e:
            capacity_info = {
                'max_fulfillment_capacity': 50000,
                'max_storage_pallets': 468,
                'max_receiving_pallets': 1000,
                'current_pallets_used': 0,
                'available_pallets': 468,
            }
        
        return capacity_info
    
    def load_orders_stats(self, orders_df: pd.DataFrame) -> Dict[str, any]:
        """
        استخراج إحصائيات الطلبات
        
        Returns:
        --------
        dict: {
            'total_orders': int,
            'monthly_orders': int,
            'inside_riyadh_orders': int,
            'outside_riyadh_orders': int,
            'avg_order_weight': float,
            'avg_skus_per_order': float,
            'return_rate': float,
            'avg_processing_hours': float
        }
        """
        self.orders_data = orders_df
        stats = {}
        
        try:
            total_orders = len(orders_df)
            
            # تصنيف الطلبات حسب الموقع
            inside_riyadh = orders_df[orders_df['DESTINATION CITY'].str.contains('رياض|Riyadh', case=False, na=False)]
            outside_riyadh = orders_df[~orders_df['DESTINATION CITY'].str.contains('رياض|Riyadh', case=False, na=False)]
            
            # حساب المتوسطات
            avg_weight = orders_df['SHIPMENT WEIGHT'].mean() if 'SHIPMENT WEIGHT' in orders_df.columns else 2.5
            avg_skus = orders_df['TOTAL SKUS'].mean() if 'TOTAL SKUS' in orders_df.columns else 3
            
            # معدل المرتجعات
            if 'RETURN STATUS' in orders_df.columns:
                returns = len(orders_df[orders_df['RETURN STATUS'].notna()])
                return_rate = (returns / total_orders * 100) if total_orders > 0 else 0
            else:
                return_rate = 5.0  # افتراضي 5%
            
            # حساب وقت التجهيز
            if 'ORDER CREATED AT' in orders_df.columns and 'ORDER PACKED AT' in orders_df.columns:
                orders_df['processing_time'] = pd.to_datetime(orders_df['ORDER PACKED AT']) - pd.to_datetime(orders_df['ORDER CREATED AT'])
                avg_processing_hours = orders_df['processing_time'].dt.total_seconds().mean() / 3600 if 'processing_time' in orders_df.columns else 2
            else:
                avg_processing_hours = 2.0
            
            stats = {
                'total_orders': total_orders,
                'monthly_orders': int(total_orders / 12),  # افتراض بيانات سنة
                'inside_riyadh_orders': len(inside_riyadh),
                'outside_riyadh_orders': len(outside_riyadh),
                'inside_riyadh_percentage': (len(inside_riyadh) / total_orders * 100) if total_orders > 0 else 50,
                'avg_order_weight': float(avg_weight),
                'avg_skus_per_order': float(avg_skus),
                'return_rate': float(return_rate),
                'avg_processing_hours': float(avg_processing_hours),
            }
            
        except Exception as e:
            stats = {
                'total_orders': 0,
                'monthly_orders': 0,
                'inside_riyadh_orders': 0,
                'outside_riyadh_orders': 0,
                'inside_riyadh_percentage': 50,
                'avg_order_weight': 2.5,
                'avg_skus_per_order': 3,
                'return_rate': 5.0,
                'avg_processing_hours': 2.0,
            }
        
        return stats
    
    # =====================================================
    # 2️⃣ حساب تكلفة الوحدة لكل سيناريو
    # =====================================================
    
    def compute_unit_cost(self, 
                          scenario: str = 'fulfillment_riyadh',
                          pl_costs: Dict = None,
                          include_return_cost: bool = True) -> Dict[str, float]:
        """
        حساب تكلفة الطلب الواحد حسب السيناريو
        
        Parameters:
        -----------
        scenario : str
            السيناريو (fulfillment_riyadh, fulfillment_outside, storage_only, etc.)
        pl_costs : dict
            التكاليف من P&L
        include_return_cost : bool
            هل نضيف تكلفة المرتجعات؟
        
        Returns:
        --------
        dict: {
            'fulfillment_cost': float,
            'storage_cost': float,
            'shipping_cost': float,
            'overhead_cost': float,
            'return_cost': float,
            'total_cost_per_order': float
        }
        """
        if pl_costs is None:
            pl_costs = self.unit_costs
        
        cost_breakdown = {
            'fulfillment_cost': 0,
            'storage_cost': 0,
            'shipping_cost': 0,
            'overhead_cost': 0,
            'return_cost': 0,
            'total_cost_per_order': 0
        }
        
        # التكاليف الأساسية
        if 'fulfillment' in scenario:
            cost_breakdown['fulfillment_cost'] = pl_costs.get('fulfillment_cost_per_order', 3.5)
        
        if 'storage' in scenario or 'fulfillment' in scenario:
            cost_breakdown['storage_cost'] = pl_costs.get('storage_cost_per_order', 1.5)
        
        # تكلفة الشحن حسب الموقع
        if 'riyadh' in scenario:
            cost_breakdown['shipping_cost'] = 8.0  # داخل الرياض
        elif 'outside' in scenario:
            cost_breakdown['shipping_cost'] = 15.0  # خارج الرياض
        else:
            cost_breakdown['shipping_cost'] = pl_costs.get('shipping_cost_per_order', 10.0)
        
        # العمومية والإدارية
        cost_breakdown['overhead_cost'] = pl_costs.get('overhead_cost_per_order', 2.0)
        
        # تكلفة المرتجعات
        if include_return_cost:
            return_rate = pl_costs.get('return_rate', 5.0) / 100
            cost_breakdown['return_cost'] = (cost_breakdown['fulfillment_cost'] + cost_breakdown['shipping_cost']) * return_rate
        
        # الإجمالي
        cost_breakdown['total_cost_per_order'] = sum(cost_breakdown.values())
        
        return cost_breakdown
    
    # =====================================================
    # 3️⃣ اقتراح السعر حسب هامش الربح
    # =====================================================
    
    def suggest_price(self, 
                      cost_per_order: float, 
                      target_margin: float = 25.0) -> Dict[str, float]:
        """
        اقتراح سعر البيع بناءً على التكلفة وهامش الربح المستهدف
        
        Formula: السعر = التكلفة ÷ (1 - هامش الربح%)
        
        Parameters:
        -----------
        cost_per_order : float
            تكلفة الطلب الواحد
        target_margin : float
            هامش الربح المستهدف (%)
        
        Returns:
        --------
        dict: {
            'cost': float,
            'target_margin_pct': float,
            'suggested_price': float,
            'profit_per_order': float,
            'actual_margin_pct': float
        }
        """
        margin_decimal = target_margin / 100
        suggested_price = cost_per_order / (1 - margin_decimal) if margin_decimal < 1 else cost_per_order * 2
        profit_per_order = suggested_price - cost_per_order
        actual_margin = (profit_per_order / suggested_price * 100) if suggested_price > 0 else 0
        
        return {
            'cost': cost_per_order,
            'target_margin_pct': target_margin,
            'suggested_price': suggested_price,
            'profit_per_order': profit_per_order,
            'actual_margin_pct': actual_margin
        }
    
    # =====================================================
    # 4️⃣ حساب الهوامش والأرباح
    # =====================================================
    
    def calculate_margins(self, 
                          selling_price: float, 
                          cost_per_order: float,
                          monthly_volume: int = 1000) -> Dict[str, float]:
        """
        حساب هوامش الربح والربح الشهري
        
        Returns:
        --------
        dict: {
            'selling_price': float,
            'cost_per_order': float,
            'profit_per_order_sar': float,
            'margin_percentage': float,
            'monthly_volume': int,
            'monthly_profit_sar': float,
            'annual_profit_sar': float
        }
        """
        profit_per_order = selling_price - cost_per_order
        margin_pct = (profit_per_order / selling_price * 100) if selling_price > 0 else 0
        monthly_profit = profit_per_order * monthly_volume
        annual_profit = monthly_profit * 12
        
        return {
            'selling_price': selling_price,
            'cost_per_order': cost_per_order,
            'profit_per_order_sar': profit_per_order,
            'margin_percentage': margin_pct,
            'monthly_volume': monthly_volume,
            'monthly_profit_sar': monthly_profit,
            'annual_profit_sar': annual_profit
        }
    
    # =====================================================
    # 5️⃣ حساب استغلال الطاقة
    # =====================================================
    
    def calculate_capacity_usage(self, 
                                  monthly_orders: int,
                                  capacity_info: Dict) -> Dict[str, any]:
        """
        حساب نسبة استغلال الطاقة والتحذيرات
        
        Returns:
        --------
        dict: {
            'monthly_orders': int,
            'max_capacity': int,
            'usage_percentage': float,
            'available_capacity': int,
            'status': str,  # 'green', 'yellow', 'red'
            'status_label': str,
            'warning': str
        }
        """
        max_capacity = capacity_info.get('max_fulfillment_capacity', 50000)
        usage_pct = (monthly_orders / max_capacity * 100) if max_capacity > 0 else 0
        available = max_capacity - monthly_orders
        
        # تحديد الحالة
        if usage_pct < 60:
            status = 'green'
            status_label = 'ممتاز - طاقة متاحة'
            warning = ''
        elif usage_pct < 85:
            status = 'yellow'
            status_label = 'تحذير - اقتراب من الحد الأقصى'
            warning = f'⚠️ نسبة الاستغلال {usage_pct:.1f}% - خطط لزيادة الطاقة قريباً'
        else:
            status = 'red'
            status_label = 'خطر - طاقة شبه مكتملة'
            warning = f'🚨 نسبة الاستغلال {usage_pct:.1f}% - يجب زيادة الطاقة فوراً!'
        
        return {
            'monthly_orders': monthly_orders,
            'max_capacity': max_capacity,
            'usage_percentage': usage_pct,
            'available_capacity': available,
            'status': status,
            'status_label': status_label,
            'warning': warning
        }
    
    # =====================================================
    # 6️⃣ تكلفة الطاقة لكل وحدة (Cost per Capacity Unit)
    # =====================================================
    
    def cost_per_capacity_unit(self, 
                                pl_costs: Dict,
                                capacity_info: Dict) -> Dict[str, float]:
        """
        حساب تكلفة كل وحدة طاقة (الطاقة المهدرة)
        
        Returns:
        --------
        dict: {
            'total_fixed_costs': float,
            'max_capacity': int,
            'cost_per_order_capacity': float,
            'cost_per_pallet_capacity': float,
            'wasted_capacity_cost': float
        }
        """
        # التكاليف الثابتة
        fixed_costs = pl_costs.get('overhead_total', 0) + (pl_costs.get('storage_total', 0) * 0.5)
        
        max_capacity = capacity_info.get('max_fulfillment_capacity', 50000)
        max_pallets = capacity_info.get('max_storage_pallets', 468)
        
        cost_per_order_cap = fixed_costs / max_capacity if max_capacity > 0 else 0
        cost_per_pallet_cap = fixed_costs / max_pallets if max_pallets > 0 else 0
        
        # الطاقة المهدرة
        current_usage = pl_costs.get('order_count', 0)
        wasted_capacity = max_capacity - current_usage
        wasted_cost = wasted_capacity * cost_per_order_cap
        
        return {
            'total_fixed_costs': fixed_costs,
            'max_capacity': max_capacity,
            'cost_per_order_capacity': cost_per_order_cap,
            'cost_per_pallet_capacity': cost_per_pallet_cap,
            'wasted_capacity_orders': wasted_capacity,
            'wasted_capacity_cost': wasted_cost
        }
    
    # =====================================================
    # 7️⃣ تحذيرات المخاطر
    # =====================================================
    
    def risk_warning(self, 
                     margin_pct: float,
                     min_margin: float = 15.0,
                     recommended_margin: float = 25.0) -> Dict[str, any]:
        """
        تحذيرات المخاطر في التسعير
        
        Returns:
        --------
        dict: {
            'margin_pct': float,
            'min_margin': float,
            'risk_level': str,  # 'safe', 'moderate', 'high'
            'warning_message': str,
            'recommendation': str
        }
        """
        if margin_pct >= recommended_margin:
            return {
                'margin_pct': margin_pct,
                'min_margin': min_margin,
                'risk_level': 'safe',
                'color': 'green',
                'warning_message': f'✅ هامش ربح ممتاز {margin_pct:.1f}%',
                'recommendation': 'السعر مناسب ويحقق ربحية جيدة'
            }
        elif margin_pct >= min_margin:
            return {
                'margin_pct': margin_pct,
                'min_margin': min_margin,
                'risk_level': 'moderate',
                'color': 'orange',
                'warning_message': f'⚠️ هامش ربح مقبول {margin_pct:.1f}% لكن أقل من المستهدف',
                'recommendation': f'حاول الوصول إلى {recommended_margin}% لزيادة الربحية'
            }
        else:
            return {
                'margin_pct': margin_pct,
                'min_margin': min_margin,
                'risk_level': 'high',
                'color': 'red',
                'warning_message': f'🚨 عرض عالي المخاطرة - هامش الربح {margin_pct:.1f}% أقل من الحد الأدنى {min_margin}%',
                'recommendation': 'يجب رفع السعر أو خفض التكاليف فوراً!'
            }
    
    # =====================================================
    # 8️⃣ تحليل السعر المثالي (Price Elasticity)
    # =====================================================
    
    def price_elasticity_analysis(self,
                                    cost_per_order: float,
                                    base_volume: int,
                                    price_range: Tuple[float, float],
                                    elasticity: float = -0.5) -> pd.DataFrame:
        """
        تحليل مرونة السعر - جرب أسعار مختلفة واحسب الربح المتوقع
        
        Parameters:
        -----------
        cost_per_order : float
            تكلفة الطلب الواحد
        base_volume : int
            الحجم الأساسي عند السعر المتوسط
        price_range : tuple
            نطاق الأسعار (min_price, max_price)
        elasticity : float
            معامل المرونة (سالب دائماً، افتراضي -0.5)
        
        Returns:
        --------
        DataFrame: جدول بتحليل الأسعار المختلفة
        """
        min_price, max_price = price_range
        base_price = (min_price + max_price) / 2
        
        # توليد 5 نقاط سعرية
        prices = np.linspace(min_price, max_price, 5)
        
        results = []
        for price in prices:
            # حساب الكمية المتوقعة بناءً على المرونة
            price_change_pct = ((price - base_price) / base_price) if base_price > 0 else 0
            volume_change_pct = elasticity * price_change_pct
            estimated_volume = int(base_volume * (1 + volume_change_pct))
            estimated_volume = max(estimated_volume, 100)  # حد أدنى 100 طلب
            
            # الحسابات المالية
            revenue = price * estimated_volume
            total_cost = cost_per_order * estimated_volume
            profit = revenue - total_cost
            margin_pct = ((price - cost_per_order) / price * 100) if price > 0 else 0
            
            results.append({
                'السعر': price,
                'الكمية المتوقعة': estimated_volume,
                'الإيراد': revenue,
                'التكلفة الكلية': total_cost,
                'الربح': profit,
                'هامش الربح %': margin_pct,
                'اختيار؟': '⭐ أفضل خيار' if profit == max([r['الربح'] for r in results + [{'الربح': profit}]]) else ''
            })
        
        return pd.DataFrame(results)
    
    # =====================================================
    # 9️⃣ تحليل عقود المؤسسات
    # =====================================================
    
    def enterprise_contract_analysis(self,
                                       cost_per_order: float,
                                       contract_price: float,
                                       expected_volume: int,
                                       minimum_monthly_fee: float = 0,
                                       volume_discount_pct: float = 0,
                                       contract_months: int = 12) -> Dict[str, float]:
        """
        تحليل عقود المؤسسات مع الحد الأدنى الشهري والخصومات
        
        Returns:
        --------
        dict: تحليل شامل للعقد
        """
        # السعر بعد الخصم
        discounted_price = contract_price * (1 - volume_discount_pct / 100)
        
        # الإيراد الشهري
        volume_revenue = discounted_price * expected_volume
        
        # هل الحد الأدنى أعلى؟
        monthly_revenue = max(volume_revenue, minimum_monthly_fee)
        
        # التكاليف والأرباح
        monthly_cost = cost_per_order * expected_volume
        monthly_profit = monthly_revenue - monthly_cost
        margin_pct = ((monthly_revenue - monthly_cost) / monthly_revenue * 100) if monthly_revenue > 0 else 0
        
        # تحليل العقد الكامل
        contract_revenue = monthly_revenue * contract_months
        contract_cost = monthly_cost * contract_months
        contract_profit = contract_revenue - contract_cost
        
        return {
            'base_price': contract_price,
            'volume_discount_pct': volume_discount_pct,
            'discounted_price': discounted_price,
            'expected_monthly_volume': expected_volume,
            'minimum_monthly_fee': minimum_monthly_fee,
            'monthly_revenue': monthly_revenue,
            'monthly_cost': monthly_cost,
            'monthly_profit': monthly_profit,
            'margin_percentage': margin_pct,
            'contract_months': contract_months,
            'total_contract_revenue': contract_revenue,
            'total_contract_profit': contract_profit,
            'average_monthly_profit': contract_profit / contract_months,
            'is_minimum_fee_applied': monthly_revenue == minimum_monthly_fee
        }


# =====================================================
# دوال مساعدة سريعة (Helper Functions)
# =====================================================

def format_currency(amount: float, currency: str = 'ريال') -> str:
    """تنسيق المبلغ بالعملة"""
    return f"{amount:,.2f} {currency}"

def format_percentage(value: float) -> str:
    """تنسيق النسبة المئوية"""
    return f"{value:.1f}%"

def get_status_color(margin_pct: float, min_margin: float = 15, recommended_margin: float = 25) -> str:
    """الحصول على لون الحالة حسب هامش الربح"""
    if margin_pct >= recommended_margin:
        return 'green'
    elif margin_pct >= min_margin:
        return 'orange'
    else:
        return 'red'
