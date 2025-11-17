"""
نموذج CMA للتسعير الإداري
Management Accounting Pricing Model
"""

class CMAPricingModel:
    def __init__(self):
        self.cost_data = {}
        self.market_data = {}
        self.results = {}
    
    def input_cost_data(self, variable_cost, fixed_cost, expected_units, capacity_units):
        """إدخال بيانات التكاليف"""
        self.cost_data = {
            'variable_cost_per_unit': variable_cost,
            'total_fixed_cost': fixed_cost,
            'expected_units_sold': expected_units,
            'capacity_units': capacity_units,
            'total_variable_cost': variable_cost * expected_units,
            'fixed_cost_per_unit': fixed_cost / expected_units if expected_units > 0 else 0
        }
        self.cost_data['total_cost_per_unit'] = (self.cost_data['variable_cost_per_unit'] + 
                                                self.cost_data['fixed_cost_per_unit'])
    
    def input_market_data(self, market_price, competitor_prices, price_elasticity, target_profit_margin):
        """إدخال بيانات السوق"""
        self.market_data = {
            'market_price': market_price,
            'competitor_avg_price': sum(competitor_prices) / len(competitor_prices) if competitor_prices else 0,
            'price_elasticity': price_elasticity,
            'target_profit_margin': target_profit_margin,
            'target_profit_per_unit': market_price * target_profit_margin
        }
    
    def calculate_cost_plus_pricing(self, markup_percentage):
        """حساب التسعير على أساس التكلفة"""
        cost_per_unit = self.cost_data['total_cost_per_unit']
        price = cost_per_unit * (1 + markup_percentage)
        
        return {
            'method': 'Cost-Plus Pricing',
            'calculated_price': round(price, 2),
            'cost_per_unit': round(cost_per_unit, 2),
            'markup_percentage': markup_percentage,
            'profit_per_unit': round(price - cost_per_unit, 2)
        }
    
    def calculate_target_pricing(self):
        """حساب التسعير المستهدف"""
        target_cost = self.market_data['market_price'] - self.market_data['target_profit_per_unit']
        current_cost = self.cost_data['total_cost_per_unit']
        cost_gap = current_cost - target_cost
        
        return {
            'method': 'Target Pricing',
            'market_price': self.market_data['market_price'],
            'target_cost': round(target_cost, 2),
            'current_cost': round(current_cost, 2),
            'cost_gap': round(cost_gap, 2),
            'required_cost_reduction_percentage': round((cost_gap / current_cost) * 100, 2) if current_cost > 0 else 0
        }
    
    def calculate_break_even(self, selling_price):
        """حساب نقطة التعادل"""
        contribution_margin = selling_price - self.cost_data['variable_cost_per_unit']
        if contribution_margin <= 0:
            return {'error': 'سعر البيع أقل من التكلفة المتغيرة'}
        
        break_even_units = self.cost_data['total_fixed_cost'] / contribution_margin
        break_even_revenue = break_even_units * selling_price
        
        return {
            'break_even_units': round(break_even_units, 2),
            'break_even_revenue': round(break_even_revenue, 2),
            'contribution_margin': round(contribution_margin, 2),
            'margin_of_safety_units': self.cost_data['expected_units_sold'] - break_even_units,
            'margin_of_safety_percentage': round(((self.cost_data['expected_units_sold'] - break_even_units) / 
                                                self.cost_data['expected_units_sold']) * 100, 2) if self.cost_data['expected_units_sold'] > 0 else 0
        }
    
    def calculate_elasticity_impact(self, price_change_percentage):
        """حساب تأثير مرونة السعر على الكمية والإيرادات"""
        if self.market_data['price_elasticity'] == 0:
            return {'error': 'مرونة السعر غير محددة'}
        
        quantity_change_percentage = self.market_data['price_elasticity'] * price_change_percentage
        new_quantity = self.cost_data['expected_units_sold'] * (1 + quantity_change_percentage)
        new_price = self.market_data['market_price'] * (1 + price_change_percentage)
        new_revenue = new_quantity * new_price
        current_revenue = self.cost_data['expected_units_sold'] * self.market_data['market_price']
        
        return {
            'price_change_percentage': price_change_percentage,
            'quantity_change_percentage': round(quantity_change_percentage * 100, 2),
            'new_quantity': round(new_quantity, 2),
            'new_price': round(new_price, 2),
            'new_revenue': round(new_revenue, 2),
            'revenue_change_percentage': round(((new_revenue - current_revenue) / current_revenue) * 100, 2) if current_revenue > 0 else 0
        }
    
    def analyze_profitability(self, selling_price):
        """تحليل الربحية الشامل"""
        revenue = self.cost_data['expected_units_sold'] * selling_price
        total_variable_cost = self.cost_data['variable_cost_per_unit'] * self.cost_data['expected_units_sold']
        total_fixed_cost = self.cost_data['total_fixed_cost']
        total_cost = total_variable_cost + total_fixed_cost
        profit = revenue - total_cost
        
        contribution_margin_per_unit = selling_price - self.cost_data['variable_cost_per_unit']
        contribution_margin_ratio = contribution_margin_per_unit / selling_price if selling_price > 0 else 0
        
        break_even = self.calculate_break_even(selling_price)
        
        return {
            'selling_price': selling_price,
            'expected_units': self.cost_data['expected_units_sold'],
            'total_revenue': round(revenue, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(profit, 2),
            'profit_margin_percentage': round((profit / revenue) * 100, 2) if revenue > 0 else 0,
            'contribution_margin_per_unit': round(contribution_margin_per_unit, 2),
            'contribution_margin_ratio': round(contribution_margin_ratio * 100, 2),
            'break_even_analysis': break_even
        }
    
    def generate_pricing_recommendation(self):
        """توليد توصيات التسعير الشاملة"""
        recommendations = []
        
        # تحليل التسعير على أساس التكلفة
        cost_plus_30 = self.calculate_cost_plus_pricing(0.30)
        cost_plus_50 = self.calculate_cost_plus_pricing(0.50)
        recommendations.append(cost_plus_30)
        recommendations.append(cost_plus_50)
        
        # تحليل التسعير المستهدف
        target_pricing = self.calculate_target_pricing()
        recommendations.append(target_pricing)
        
        # تحليل نقطة التعادل عند أسعار مختلفة
        prices_to_analyze = [
            self.market_data['market_price'],
            cost_plus_30['calculated_price'],
            cost_plus_50['calculated_price'],
            self.market_data['competitor_avg_price']
        ]
        
        profitability_analysis = []
        for price in prices_to_analyze:
            if price > 0:
                analysis = self.analyze_profitability(price)
                profitability_analysis.append(analysis)
        
        # تحليل تأثير تغيير السعر
        elasticity_analysis = {}
        if self.market_data['price_elasticity'] != 0:
            for change in [-0.10, -0.05, 0.05, 0.10]:  # -10%, -5%, +5%, +10%
                elasticity_analysis[f"{int(change*100)}%"] = self.calculate_elasticity_impact(change)
        
        return {
            'recommendations': recommendations,
            'profitability_analysis': profitability_analysis,
            'elasticity_analysis': elasticity_analysis,
            'summary': self._generate_summary(profitability_analysis)
        }
    
    def _generate_summary(self, profitability_analysis):
        """توليد ملخص التوصيات"""
        if not profitability_analysis:
            return "لا توجد بيانات كافية لتوليد التوصيات"
        
        # إيجاد السعر الذي يحقق أعلى ربح
        best_profit = max(analysis['total_profit'] for analysis in profitability_analysis)
        best_analysis = next(analysis for analysis in profitability_analysis if analysis['total_profit'] == best_profit)
        
        summary = {
            'best_price': best_analysis['selling_price'],
            'best_profit': best_analysis['total_profit'],
            'profit_margin': best_analysis['profit_margin_percentage'],
            'break_even_units': best_analysis['break_even_analysis']['break_even_units'],
            'margin_of_safety': best_analysis['break_even_analysis']['margin_of_safety_percentage'],
            'contribution_margin': best_analysis['contribution_margin_ratio']
        }
        
        return summary
