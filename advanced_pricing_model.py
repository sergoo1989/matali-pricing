"""
نموذج التسعير المتقدم - Advanced Pricing Model
يتضمن استراتيجيات تسعير متعددة ومتقدمة
"""

import json
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AdvancedPricingModel:
    def __init__(self, product_name="منتج"):
        self.product_name = product_name
        self.cost_data = {}
        self.market_data = {}
        self.pricing_history = []
        self.competitor_data = []
        self.scenarios = {}
        
    def input_detailed_cost_data(self, cost_structure):
        """إدخال بيانات تكاليف مفصلة"""
        self.cost_data = {
            # التكاليف المباشرة
            'direct_materials': cost_structure.get('direct_materials', 0),
            'direct_labor': cost_structure.get('direct_labor', 0),
            'variable_overhead': cost_structure.get('variable_overhead', 0),
            
            # التكاليف غير المباشرة
            'fixed_overhead': cost_structure.get('fixed_overhead', 0),
            'rnd_costs': cost_structure.get('rnd_costs', 0),
            'marketing_costs': cost_structure.get('marketing_costs', 0),
            'administrative_costs': cost_structure.get('administrative_costs', 0),
            
            # بيانات الإنتاج
            'expected_units': cost_structure.get('expected_units', 0),
            'capacity_units': cost_structure.get('capacity_units', 0),
            'production_cycle_days': cost_structure.get('production_cycle_days', 30)
        }
        
        # حساب التكاليف الإجمالية
        self._calculate_total_costs()
    
    def _calculate_total_costs(self):
        """حساب التكاليف الإجمالية"""
        # التكاليف المتغيرة للوحدة
        self.cost_data['variable_cost_per_unit'] = (
            self.cost_data['direct_materials'] + 
            self.cost_data['direct_labor'] + 
            self.cost_data['variable_overhead']
        )
        
        # التكاليف الثابتة الإجمالية
        self.cost_data['total_fixed_costs'] = (
            self.cost_data['fixed_overhead'] +
            self.cost_data['rnd_costs'] +
            self.cost_data['marketing_costs'] +
            self.cost_data['administrative_costs']
        )
        
        # التكاليف الثابتة للوحدة
        if self.cost_data['expected_units'] > 0:
            self.cost_data['fixed_cost_per_unit'] = (
                self.cost_data['total_fixed_costs'] / self.cost_data['expected_units']
            )
        else:
            self.cost_data['fixed_cost_per_unit'] = 0
        
        # التكلفة الكلية للوحدة
        self.cost_data['total_cost_per_unit'] = (
            self.cost_data['variable_cost_per_unit'] + 
            self.cost_data['fixed_cost_per_unit']
        )
    
    def input_market_analysis(self, market_analysis):
        """إدخال تحليل السوق المتقدم"""
        self.market_data = {
            'current_market_price': market_analysis.get('current_market_price', 0),
            'price_elasticity': market_analysis.get('price_elasticity', -1.5),
            'market_growth_rate': market_analysis.get('market_growth_rate', 0.05),
            'market_share_target': market_analysis.get('market_share_target', 0.1),
            'customer_segments': market_analysis.get('customer_segments', {}),
            'seasonality_factor': market_analysis.get('seasonality_factor', 1.0),
            'product_lifecycle_stage': market_analysis.get('product_lifecycle_stage', 'growth')
        }
    
    def add_competitor(self, name, price, market_share, cost_structure=None):
        """إضافة بيانات منافس"""
        competitor = {
            'name': name,
            'price': price,
            'market_share': market_share,
            'cost_structure': cost_structure or {}
        }
        self.competitor_data.append(competitor)
    
    def calculate_lifecycle_pricing(self):
        """تسعير بناءً على مرحلة دورة حياة المنتج"""
        lifecycle_stage = self.market_data.get('product_lifecycle_stage', 'growth')
        base_cost = self.cost_data.get('total_cost_per_unit', 0)
        
        lifecycle_strategies = {
            'introduction': {
                'description': 'مرحلة التقديم - استراتيجية القشط',
                'markup_range': (0.4, 0.6),
                'focus': 'استرداد تكاليف R&D'
            },
            'growth': {
                'description': 'مرحلة النمو - استراتيجية الاختراق', 
                'markup_range': (0.2, 0.35),
                'focus': 'كسب حصة سوقية'
            },
            'maturity': {
                'description': 'مرحلة النضج - المنافسة على السعر',
                'markup_range': (0.15, 0.25),
                'focus': 'الحفاظ على الحصة السوقية'
            },
            'decline': {
                'description': 'مرحلة الانحدار - تقليل الخسائر',
                'markup_range': (0.05, 0.15),
                'focus': 'تعظيم التدفق النقدي'
            }
        }
        
        strategy = lifecycle_strategies.get(lifecycle_stage, lifecycle_strategies['growth'])
        min_markup, max_markup = strategy['markup_range']
        
        return {
            'stage': lifecycle_stage,
            'strategy': strategy['description'],
            'focus': strategy['focus'],
            'recommended_markup_range': f"{min_markup*100}% - {max_markup*100}%",
            'price_range': {
                'min': base_cost * (1 + min_markup),
                'max': base_cost * (1 + max_markup)
            }
        }
    
    def calculate_psychological_pricing(self, base_price):
        """تسعير نفسي"""
        psychological_prices = {}
        
        psychological_prices['ending_999'] = {
            'description': 'تنتهي بـ 9.99 (تأثير اليسار)',
            'price': round(base_price - 0.01, 2),
            'perceived_value': 'جيد للسلع الاستهلاكية'
        }
        
        psychological_prices['prestige_pricing'] = {
            'description': 'تسعير متميز (أرقام كاملة)',
            'price': round(base_price),
            'perceived_value': 'مناسب للسلع الفاخرة'
        }
        
        if base_price > 10:
            psychological_prices['charm_pricing'] = {
                'description': 'تسعير جذاب',
                'price': round(base_price - 0.01, 2),
                'perceived_value': 'يخلق وهم الدفع الأقل'
            }
        
        return psychological_prices
    
    def calculate_discount_strategy(self, base_price):
        """استراتيجية الخصومات"""
        discount_strategies = {
            'quantity_discounts': {
                'tier_1': {'min_quantity': 10, 'discount': 0.05},
                'tier_2': {'min_quantity': 50, 'discount': 0.10},
                'tier_3': {'min_quantity': 100, 'discount': 0.15}
            },
            'seasonal_discount': {
                'off_peak': {'discount': 0.10, 'season': 'منخفض'},
                'clearance': {'discount': 0.20, 'season': 'نهاية الموسم'}
            }
        }
        
        discounted_prices = {}
        for discount_type, strategies in discount_strategies.items():
            discounted_prices[discount_type] = {}
            for strategy_name, strategy in strategies.items():
                if 'discount' in strategy:
                    discounted_price = base_price * (1 - strategy['discount'])
                    discounted_prices[discount_type][strategy_name] = {
                        'original_price': base_price,
                        'discounted_price': round(discounted_price, 2),
                        'discount_percentage': strategy['discount'] * 100,
                        'conditions': strategy
                    }
        
        return discounted_prices
    
    def create_pricing_scenario(self, scenario_name, assumptions):
        """إنشاء سيناريوهات تسعير مختلفة"""
        self.scenarios[scenario_name] = {
            'assumptions': assumptions,
            'created_at': datetime.now(),
            'analysis': self._analyze_scenario(assumptions)
        }
        
        return self.scenarios[scenario_name]
    
    def _analyze_scenario(self, assumptions):
        """تحليل السيناريو"""
        base_price = assumptions.get('base_price', self.cost_data.get('total_cost_per_unit', 0) * 1.3)
        volume = assumptions.get('volume', self.cost_data.get('expected_units', 0))
        
        revenue = base_price * volume
        total_cost = (self.cost_data.get('variable_cost_per_unit', 0) * volume + 
                     self.cost_data.get('total_fixed_costs', 0))
        profit = revenue - total_cost
        
        # تحليل الحساسية
        sensitivity = {}
        price_elasticity = self.market_data.get('price_elasticity', -1.5)
        
        for change in [-0.1, -0.05, 0.05, 0.1]:
            new_volume = volume * (1 + change * price_elasticity)
            new_revenue = base_price * (1 + change) * new_volume
            new_profit = new_revenue - total_cost
            sensitivity[f"{change*100:+.0f}%"] = {
                'new_profit': round(new_profit, 2),
                'profit_change_percentage': round(((new_profit - profit) / profit) * 100, 2) if profit != 0 else 0
            }
        
        variable_cost = self.cost_data.get('variable_cost_per_unit', 0)
        break_even = self.cost_data.get('total_fixed_costs', 0) / (base_price - variable_cost) if (base_price - variable_cost) > 0 else float('inf')
        
        return {
            'base_price': base_price,
            'expected_volume': volume,
            'revenue': round(revenue, 2),
            'total_cost': round(total_cost, 2),
            'profit': round(profit, 2),
            'profit_margin': round((profit / revenue) * 100, 2) if revenue > 0 else 0,
            'sensitivity_analysis': sensitivity,
            'break_even_point': break_even
        }
    
    def generate_comprehensive_report(self):
        """توليد تقرير شامل"""
        if not self.cost_data or not self.market_data:
            return {"error": "بيانات غير كاملة. يرجى إدخال بيانات التكاليف والسوق أولاً."}
        
        base_price = self.cost_data.get('total_cost_per_unit', 0) * 1.3
        
        report = {
            'product_name': self.product_name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cost_analysis': self.cost_data,
            'market_analysis': self.market_data,
            'lifecycle_pricing': self.calculate_lifecycle_pricing(),
            'competitor_analysis': self.competitor_data,
            'scenarios': self.scenarios,
            'recommendations': {
                'psychological_pricing': self.calculate_psychological_pricing(base_price),
                'discount_strategies': self.calculate_discount_strategy(base_price)
            }
        }
        
        return report
