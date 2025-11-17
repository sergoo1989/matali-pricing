import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize
import json
from advanced_pricing_model import AdvancedPricingModel

class EnterprisePricingModel(AdvancedPricingModel):
    """نموذج تسعير متقدم للمؤسسات مع تحليل شامل"""
    
    def __init__(self, product_name="منتج"):
        super().__init__(product_name)
        self.sales_data = pd.DataFrame()
        self.customer_segments = {}
        self.promotional_campaigns = []
        self.regulatory_constraints = {}
        self.risk_factors = {}
        
    def integrate_sales_history(self, sales_data):
        """دمج بيانات المبيعات التاريخية"""
        self.sales_data = sales_data
        self._analyze_sales_patterns()
    
    def _analyze_sales_patterns(self):
        """تحليل أنماط المبيعات التاريخية"""
        if self.sales_data.empty:
            return
            
        # تحليل الموسمية
        self.sales_data['month'] = self.sales_data['date'].dt.month
        monthly_patterns = self.sales_data.groupby('month')['quantity'].mean()
        
        # تحليل استجابة السعر
        price_elasticity_historical = self._calculate_historical_elasticity()
        
        self.market_data.update({
            'historical_monthly_patterns': monthly_patterns.to_dict(),
            'historical_price_elasticity': price_elasticity_historical
        })
    
    def _calculate_historical_elasticity(self):
        """حساب مرونة السعر من البيانات التاريخية"""
        if len(self.sales_data) < 2:
            return self.market_data.get('price_elasticity', -1.5)
            
        # حساب التغيرات في السعر والكمية
        price_changes = self.sales_data['price'].pct_change().dropna()
        quantity_changes = self.sales_data['quantity'].pct_change().dropna()
        
        if len(price_changes) > 0:
            elasticity = (quantity_changes.mean() / price_changes.mean() 
                        if price_changes.mean() != 0 else -1.5)
            return max(elasticity, -5.0)  # حد أقصى للمرونة
        return -1.5
    
    def define_customer_segments(self, segments):
        """تحديد شرائح العملاء"""
        self.customer_segments = segments
        
    def calculate_segmented_pricing(self):
        """حساب التسعير المتمايز للشرائح"""
        segmented_prices = {}
        base_cost = self.cost_data.get('total_cost_per_unit', 0)
        
        if base_cost == 0:
            return {'error': 'يجب إدخال بيانات التكاليف أولاً'}
        
        for segment_name, segment_data in self.customer_segments.items():
            willingness_to_pay = segment_data.get('willingness_to_pay_multiplier', 1.0)
            price_sensitivity = segment_data.get('price_sensitivity', 1.0)
            segment_size = segment_data.get('size', 0)
            
            # حساب السعر الأمثل للشريحة
            optimal_price = self._optimize_segment_price(
                base_cost, willingness_to_pay, price_sensitivity, segment_size
            )
            
            segmented_prices[segment_name] = {
                'optimal_price': optimal_price,
                'target_margin': (optimal_price - base_cost) / optimal_price * 100 if optimal_price > 0 else 0,
                'expected_volume': segment_size,
                'willingness_to_pay': willingness_to_pay
            }
        
        return segmented_prices
    
    def _optimize_segment_price(self, base_cost, wtp_multiplier, sensitivity, size):
        """تحسين السعر للشريحة"""
        def profit_function(price):
            # دالة الطلب بناءً على مرونة السعر
            demand = size * (1 + sensitivity * (wtp_multiplier - price/base_cost))
            demand = max(demand, 0)
            revenue = price * demand
            cost = base_cost * demand
            return -(revenue - cost)  # سالب لأننا نريد التعظيم
        
        # البحث عن السعر الأمثل
        initial_price = base_cost * wtp_multiplier
        result = minimize(profit_function, initial_price, 
                         bounds=[(base_cost * 1.05, base_cost * 3.0)])
        
        return result.x[0] if result.success else initial_price
    
    def add_promotional_campaign(self, campaign):
        """إضافة حملة ترويجية"""
        self.promotional_campaigns.append({
            **campaign,
            'created_at': datetime.now(),
            'impact_assessment': self._assess_promotional_impact(campaign)
        })
    
    def _assess_promotional_impact(self, campaign):
        """تقييم تأثير الحملة الترويجية"""
        base_demand = self.cost_data.get('expected_units', 0)
        discount = campaign.get('discount_percentage', 0)
        duration = campaign.get('duration_days', 30)
        reach = campaign.get('reach_percentage', 0.1)
        
        # حساب الزيادة في الطلب
        demand_increase = base_demand * reach * (discount * 2)  # افتراض: كل 1% خصم = 2% زيادة طلب
        
        # حساب تأثير الربحية
        market_price = self.market_data.get('current_market_price', 0)
        original_revenue = market_price * base_demand
        promotional_price = market_price * (1 - discount/100)
        promotional_revenue = promotional_price * (base_demand + demand_increase)
        
        # حساب التكاليف الإضافية
        additional_costs = campaign.get('additional_costs', 0)
        
        impact = {
            'expected_demand_increase': demand_increase,
            'revenue_impact': promotional_revenue - original_revenue,
            'incremental_customers': demand_increase,
            'campaign_roi': (promotional_revenue - original_revenue - additional_costs) / additional_costs 
            if additional_costs > 0 else float('inf')
        }
        
        return impact
    
    def set_regulatory_constraints(self, constraints):
        """تعيين القيود التنظيمية"""
        self.regulatory_constraints = constraints
    
    def check_regulatory_compliance(self, proposed_price):
        """فحص التوافق التنظيمي"""
        violations = []
        
        # فحص الحد الأقصى للربح
        max_profit_margin = self.regulatory_constraints.get('max_profit_margin')
        cost = self.cost_data.get('total_cost_per_unit', 0)
        
        if cost == 0:
            return {'is_compliant': False, 'violations': ['يجب إدخال بيانات التكاليف أولاً'], 'required_adjustments': []}
        
        profit_margin = (proposed_price - cost) / proposed_price * 100 if proposed_price > 0 else 0
        
        if max_profit_margin and profit_margin > max_profit_margin:
            violations.append(f"هامش الربح ({profit_margin:.1f}%) يتجاوز الحد المسموح ({max_profit_margin}%)")
        
        # فحص التسعير الافتراسي
        min_price_ratio = self.regulatory_constraints.get('min_price_ratio_to_cost', 1.0)
        if proposed_price < cost * min_price_ratio:
            violations.append(f"السعر أقل من الحد الأدنى المسموح به")
        
        return {
            'is_compliant': len(violations) == 0,
            'violations': violations,
            'required_adjustments': self._suggest_regulatory_adjustments(violations, proposed_price)
        }
    
    def _suggest_regulatory_adjustments(self, violations, proposed_price):
        """اقتراح تعديلات للتوافق التنظيمي"""
        adjustments = []
        cost = self.cost_data.get('total_cost_per_unit', 0)
        
        for violation in violations:
            if "هامش الربح" in violation:
                max_margin = self.regulatory_constraints.get('max_profit_margin', 30)
                adjusted_price = cost / (1 - max_margin/100)
                adjustments.append(f"خفض السعر إلى {adjusted_price:.2f} ر.س")
            
            if "الحد الأدنى" in violation:
                min_ratio = self.regulatory_constraints.get('min_price_ratio_to_cost', 1.0)
                adjusted_price = cost * min_ratio
                adjustments.append(f"رفع السعر إلى {adjusted_price:.2f} ر.س")
        
        return adjustments
    
    def assess_market_risks(self):
        """تقييم مخاطر السوق"""
        risks = {
            'competitive_risks': self._assess_competitive_risks(),
            'demand_risks': self._assess_demand_risks(),
            'regulatory_risks': self._assess_regulatory_risks(),
            'supply_chain_risks': self._assess_supply_chain_risks()
        }
        
        # حساب درجة المخاطر الإجمالية
        total_risk_score = sum(risk['score'] for risk in risks.values()) / len(risks)
        
        self.risk_factors = {
            **risks,
            'overall_risk_score': total_risk_score,
            'risk_level': 'منخفض' if total_risk_score < 3 else 'متوسط' if total_risk_score < 7 else 'مرتفع'
        }
        
        return self.risk_factors
    
    def _assess_competitive_risks(self):
        """تقييم المخاطر التنافسية"""
        competitor_count = len(self.competitor_data)
        price_variability = np.std([comp['price'] for comp in self.competitor_data]) if self.competitor_data else 0
        
        risk_score = min(competitor_count * 0.5 + price_variability * 0.1, 10)
        
        return {
            'score': risk_score,
            'factors': [
                f"عدد المنافسين: {competitor_count}",
                f"تقلب الأسعار: {price_variability:.2f}"
            ]
        }
    
    def _assess_demand_risks(self):
        """تقييم مخاطر الطلب"""
        elasticity = abs(self.market_data.get('price_elasticity', -1.5))
        market_growth = self.market_data.get('market_growth_rate', 0.05)
        
        risk_score = (1/elasticity) * 5 + (1 - min(market_growth, 0.2)) * 5
        
        return {
            'score': risk_score,
            'factors': [
                f"مرونة الطلب: {elasticity:.2f}",
                f"معدل نمو السوق: {market_growth:.2%}"
            ]
        }
    
    def _assess_regulatory_risks(self):
        """تقييم المخاطر التنظيمية"""
        constraint_count = len(self.regulatory_constraints)
        risk_score = min(constraint_count * 2, 10)
        
        return {
            'score': risk_score,
            'factors': [f"عدد القيود التنظيمية: {constraint_count}"]
        }
    
    def _assess_supply_chain_risks(self):
        """تقييم مخاطر سلسلة التوريد"""
        # افتراض بسيط بناءً على هيكل التكاليف
        variable_ratio = self.cost_data.get('variable_cost_per_unit', 0) / max(self.cost_data.get('total_cost_per_unit', 1), 1)
        risk_score = variable_ratio * 10  # كلما زادت النسبة المتغيرة زادت المخاطر
        
        return {
            'score': risk_score,
            'factors': [f"نسبة التكاليف المتغيرة: {variable_ratio:.1%}"]
        }
    
    def simulate_economic_scenarios(self, scenarios):
        """محاكاة سيناريوهات اقتصادية مختلفة"""
        scenario_results = {}
        
        for scenario_name, assumptions in scenarios.items():
            # تعديل المعطيات بناءً على السيناريو
            adjusted_market_data = self._adjust_for_scenario(assumptions)
            
            # حساب السعر المقترح
            base_cost = self.cost_data.get('total_cost_per_unit', 0)
            markup = 0.3
            recommended_price = base_cost * (1 + markup)
            
            scenario_results[scenario_name] = {
                'assumptions': assumptions,
                'recommended_price': recommended_price,
                'expected_profit_change': self._calculate_profit_impact(assumptions),
                'risk_level': self._assess_scenario_risk(assumptions)
            }
        
        return scenario_results
    
    def _adjust_for_scenario(self, assumptions):
        """تعديل بيانات السوق بناءً على السيناريو"""
        adjusted_data = self.market_data.copy()
        
        # تعديل مرونة الطلب
        if 'demand_shock' in assumptions:
            adjusted_data['price_elasticity'] = adjusted_data.get('price_elasticity', -1.5) * (1 + assumptions['demand_shock'])
        
        # تعديل معدل النمو
        if 'growth_change' in assumptions:
            adjusted_data['market_growth_rate'] = adjusted_data.get('market_growth_rate', 0.05) + assumptions['growth_change']
        
        return adjusted_data
    
    def _calculate_profit_impact(self, assumptions):
        """حساب تأثير السيناريو على الربح"""
        demand_shock = assumptions.get('demand_shock', 0)
        growth_change = assumptions.get('growth_change', 0)
        
        # تقدير بسيط
        impact = (demand_shock + growth_change) * 100
        return f"{impact:+.1f}%"
    
    def _assess_scenario_risk(self, assumptions):
        """تقييم مخاطر السيناريو"""
        demand_shock = abs(assumptions.get('demand_shock', 0))
        growth_change = abs(assumptions.get('growth_change', 0))
        
        risk_score = (demand_shock + growth_change) * 10
        
        if risk_score < 3:
            return 'منخفض'
        elif risk_score < 7:
            return 'متوسط'
        else:
            return 'مرتفع'
    
    def generate_ai_pricing_recommendations(self):
        """توليد توصيات تسعير باستخدام مفاهيم الذكاء الاصطناعي"""
        # تحليل متعدد الأبعاد
        factors = {
            'cost_structure': self._analyze_cost_efficiency(),
            'market_position': self._analyze_market_position(),
            'competitive_landscape': self._analyze_competitive_landscape(),
            'customer_behavior': self._analyze_customer_behavior()
        }
        
        # خوارزمية توصية متقدمة
        recommendation_engine = PricingRecommendationEngine(factors)
        recommendations = recommendation_engine.generate_recommendations()
        
        return {
            'factors_analysis': factors,
            'ai_recommendations': recommendations,
            'confidence_score': recommendation_engine.calculate_confidence(),
            'implementation_priority': recommendation_engine.prioritize_recommendations()
        }
    
    def _analyze_cost_efficiency(self):
        """تحليل كفاءة التكاليف"""
        variable_cost = self.cost_data.get('variable_cost_per_unit', 0)
        total_cost = self.cost_data.get('total_cost_per_unit', 1)
        
        cost_ratio = variable_cost / max(total_cost, 1)
        efficiency_score = 1 - cost_ratio  # كلما ارتفع أفضل
        
        return {
            'score': efficiency_score,
            'rating': 'مرتفع' if efficiency_score > 0.7 else 'متوسط' if efficiency_score > 0.5 else 'منخفض',
            'suggestions': [
                "تحسين كفاءة الإنتاج" if efficiency_score < 0.6 else "الحفاظ على الكفاءة الحالية"
            ]
        }
    
    def _analyze_market_position(self):
        """تحليل الموقف السوقي"""
        market_share = self.market_data.get('market_share_target', 0.1)
        
        return {
            'score': market_share,
            'rating': 'قوي' if market_share > 0.3 else 'متوسط' if market_share > 0.15 else 'ضعيف',
            'suggestions': ['تعزيز الموقف السوقي' if market_share < 0.2 else 'الحفاظ على الحصة السوقية']
        }
    
    def _analyze_competitive_landscape(self):
        """تحليل المنافسة"""
        competitor_count = len(self.competitor_data)
        
        return {
            'score': 1 - min(competitor_count / 10, 1),
            'rating': 'تنافسية منخفضة' if competitor_count < 3 else 'تنافسية متوسطة' if competitor_count < 6 else 'تنافسية عالية',
            'suggestions': ['مراقبة المنافسين باستمرار']
        }
    
    def _analyze_customer_behavior(self):
        """تحليل سلوك العملاء"""
        elasticity = abs(self.market_data.get('price_elasticity', -1.5))
        
        return {
            'score': 1 / elasticity if elasticity > 0 else 0.5,
            'rating': 'حساس للسعر' if elasticity > 2 else 'متوسط الحساسية' if elasticity > 1 else 'غير حساس',
            'suggestions': ['استراتيجية تسعير مرنة' if elasticity > 2 else 'استراتيجية تسعير قيمية']
        }


class PricingRecommendationEngine:
    """محرك توصيات التسعير بالذكاء الاصطناعي"""
    
    def __init__(self, factors):
        self.factors = factors
        
    def generate_recommendations(self):
        """توليد التوصيات"""
        recommendations = []
        
        # تحليل هيكل التكاليف
        cost_efficiency = self.factors['cost_structure']['score']
        if cost_efficiency < 0.5:
            recommendations.append({
                'type': 'cost_optimization',
                'priority': 'high',
                'action': 'مراجعة هيكل التكاليف وخفض التكاليف الثابتة',
                'expected_impact': 'مرتفع'
            })
        
        # تحليل الموقف التنافسي
        market_position = self.factors['market_position']['score']
        if market_position < 0.3:
            recommendations.append({
                'type': 'competitive_positioning',
                'priority': 'high',
                'action': 'اعتماد استراتيجية اختراق السوق بأسعار تنافسية',
                'expected_impact': 'مرتفع'
            })
        
        # تحليل المنافسة
        competitive_score = self.factors['competitive_landscape']['score']
        if competitive_score < 0.4:
            recommendations.append({
                'type': 'differentiation',
                'priority': 'medium',
                'action': 'التركيز على التميز والقيمة المضافة',
                'expected_impact': 'متوسط'
            })
        
        # تحليل سلوك العملاء
        customer_score = self.factors['customer_behavior']['score']
        if customer_score > 0.5:
            recommendations.append({
                'type': 'value_pricing',
                'priority': 'medium',
                'action': 'استراتيجية تسعير قائمة على القيمة',
                'expected_impact': 'متوسط'
            })
        
        return recommendations
    
    def calculate_confidence(self):
        """حساب درجة الثقة في التوصيات"""
        # حساب متوسط درجات الثقة من جميع العوامل
        scores = [factor['score'] for factor in self.factors.values() 
                 if 'score' in factor]
        return np.mean(scores) if scores else 0.5
    
    def prioritize_recommendations(self):
        """ترتيب الأولويات للتوصيات"""
        # خوارزمية ترتيب الأولويات
        return sorted(self.generate_recommendations(), 
                     key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 0), 
                     reverse=True)


def create_sample_sales_data():
    """إنشاء بيانات مبيعات نموذجية للاختبار"""
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='M')
    sales_data = pd.DataFrame({
        'date': dates,
        'quantity': np.random.randint(1000, 5000, len(dates)),
        'price': np.random.uniform(100, 200, len(dates)),
        'promotion': np.random.choice([0, 1], len(dates), p=[0.7, 0.3])
    })
    return sales_data
