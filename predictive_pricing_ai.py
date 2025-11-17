import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class PredictivePricingAI:
    """نموذج تسعير تنبؤي متقدم باستخدام الذكاء الاصطناعي"""
    
    def __init__(self):
        self.models = {}
        self.training_data = pd.DataFrame()
        self.model_accuracy = {}
        self.feature_importance = {}
        
    def integrate_machine_learning(self, historical_data):
        """دمج تعلم الآلة للتنبؤ بالأسعار"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, r2_score
        except ImportError:
            return {
                'error': 'يجب تثبيت scikit-learn أولاً: pip install scikit-learn',
                'accuracy': 0
            }
        
        if historical_data.empty:
            return {
                'error': 'لا توجد بيانات تاريخية كافية',
                'accuracy': 0
            }
        
        # تحضير البيانات
        features = ['cost', 'competitor_price', 'demand', 'seasonality', 'promotion']
        target = 'optimal_price'
        
        # التحقق من وجود الأعمدة المطلوبة
        missing_cols = [col for col in features + [target] if col not in historical_data.columns]
        if missing_cols:
            return {
                'error': f'أعمدة مفقودة: {", ".join(missing_cols)}',
                'accuracy': 0
            }
        
        X = historical_data[features]
        y = historical_data[target]
        
        # تقسيم البيانات
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # تدريب النموذج
        self.models['price_predictor'] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.models['price_predictor'].fit(X_train, y_train)
        
        # تقييم النموذج
        y_pred = self.models['price_predictor'].predict(X_test)
        accuracy = self.models['price_predictor'].score(X_test, y_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # حفظ أهمية المتغيرات
        self.feature_importance = dict(zip(features, self.models['price_predictor'].feature_importances_))
        
        self.model_accuracy = {
            'r2_score': r2,
            'accuracy_percentage': accuracy * 100,
            'mean_absolute_error': mae,
            'samples_trained': len(X_train),
            'samples_tested': len(X_test)
        }
        
        return {
            'success': True,
            'accuracy': accuracy,
            'mae': mae,
            'r2_score': r2,
            'feature_importance': self.feature_importance
        }
    
    def predict_optimal_price(self, current_conditions):
        """التنبؤ بالسعر الأمثل"""
        if 'price_predictor' not in self.models:
            return {
                'error': 'يجب تدريب النموذج أولاً',
                'predicted_price': None
            }
        
        # تحويل الشروط الحالية لتنسيق مناسب
        if isinstance(current_conditions, dict):
            features = ['cost', 'competitor_price', 'demand', 'seasonality', 'promotion']
            conditions_array = [[current_conditions.get(f, 0) for f in features]]
        else:
            conditions_array = [current_conditions]
        
        prediction = self.models['price_predictor'].predict(conditions_array)
        
        # حساب نطاق الثقة (تقريبي)
        # في Random Forest يمكننا استخدام تباين التنبؤات من الأشجار المختلفة
        predictions_per_tree = []
        for tree in self.models['price_predictor'].estimators_:
            predictions_per_tree.append(tree.predict(conditions_array)[0])
        
        std_dev = np.std(predictions_per_tree)
        confidence_interval = {
            'lower': prediction[0] - 1.96 * std_dev,
            'upper': prediction[0] + 1.96 * std_dev
        }
        
        return {
            'predicted_price': prediction[0],
            'confidence_interval': confidence_interval,
            'confidence_range': f"{confidence_interval['lower']:.2f} - {confidence_interval['upper']:.2f}",
            'std_deviation': std_dev
        }
    
    def demand_forecasting(self, demand_history, steps=30):
        """التنبؤ بالطلب باستخدام ARIMA"""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            from statsmodels.tsa.stattools import adfuller
        except ImportError:
            return {
                'error': 'يجب تثبيت statsmodels أولاً: pip install statsmodels',
                'forecast': []
            }
        
        if len(demand_history) < 10:
            return {
                'error': 'البيانات التاريخية غير كافية (يجب 10 نقاط على الأقل)',
                'forecast': []
            }
        
        try:
            # تحويل إلى Series إذا كان DataFrame
            if isinstance(demand_history, pd.DataFrame):
                if 'demand' in demand_history.columns:
                    demand_series = demand_history['demand']
                else:
                    demand_series = demand_history.iloc[:, 0]
            else:
                demand_series = pd.Series(demand_history)
            
            # اختبار الاستقرارية
            adf_result = adfuller(demand_series)
            is_stationary = adf_result[1] < 0.05
            
            # تطبيق نموذج ARIMA
            # استخدام معاملات بسيطة - يمكن تحسينها لاحقاً
            order = (1, 1, 1) if not is_stationary else (1, 0, 1)
            
            model = ARIMA(demand_series, order=order)
            fitted_model = model.fit()
            
            # التنبؤ
            forecast = fitted_model.forecast(steps=steps)
            
            # حساب فترة الثقة
            forecast_df = fitted_model.get_forecast(steps=steps)
            confidence_intervals = forecast_df.conf_int()
            
            return {
                'success': True,
                'forecast': forecast.tolist(),
                'confidence_intervals': {
                    'lower': confidence_intervals.iloc[:, 0].tolist(),
                    'upper': confidence_intervals.iloc[:, 1].tolist()
                },
                'model_summary': {
                    'aic': fitted_model.aic,
                    'bic': fitted_model.bic,
                    'order': order,
                    'is_stationary': is_stationary
                }
            }
            
        except Exception as e:
            return {
                'error': f'خطأ في التنبؤ: {str(e)}',
                'forecast': []
            }
    
    def price_elasticity_learning(self, price_demand_data):
        """تعلم مرونة السعر من البيانات التاريخية"""
        try:
            from sklearn.linear_model import LinearRegression
        except ImportError:
            return {'error': 'يجب تثبيت scikit-learn'}
        
        if len(price_demand_data) < 5:
            return {'error': 'بيانات غير كافية'}
        
        # حساب نسب التغير
        price_changes = price_demand_data['price'].pct_change().dropna()
        demand_changes = price_demand_data['demand'].pct_change().dropna()
        
        if len(price_changes) < 2:
            return {'error': 'بيانات غير كافية لحساب المرونة'}
        
        # تدريب نموذج خطي
        X = price_changes.values.reshape(-1, 1)
        y = demand_changes.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        elasticity = model.coef_[0]
        
        return {
            'elasticity': elasticity,
            'interpretation': self._interpret_elasticity(elasticity),
            'r2_score': model.score(X, y)
        }
    
    def _interpret_elasticity(self, elasticity):
        """تفسير مرونة السعر"""
        abs_elasticity = abs(elasticity)
        
        if abs_elasticity > 1:
            category = "مرن (Elastic)"
            meaning = "الطلب حساس جداً للتغيرات في السعر"
            recommendation = "تخفيضات صغيرة في السعر قد تزيد الإيرادات بشكل كبير"
        elif abs_elasticity == 1:
            category = "مرن وحدوياً (Unit Elastic)"
            meaning = "التغير في السعر يؤدي لتغير مماثل في الطلب"
            recommendation = "التغييرات في السعر لها تأثير متوازن"
        else:
            category = "غير مرن (Inelastic)"
            meaning = "الطلب غير حساس كثيراً للتغيرات في السعر"
            recommendation = "يمكن زيادة الأسعار لزيادة الإيرادات"
        
        return {
            'category': category,
            'meaning': meaning,
            'recommendation': recommendation,
            'value': elasticity
        }
    
    def competitor_price_tracking(self, competitor_data, time_window=30):
        """تتبع وتحليل أسعار المنافسين"""
        if competitor_data.empty:
            return {'error': 'لا توجد بيانات منافسين'}
        
        analysis = {
            'competitors': {}
        }
        
        for competitor in competitor_data['competitor'].unique():
            comp_data = competitor_data[competitor_data['competitor'] == competitor]
            
            # تحليل الاتجاه
            if len(comp_data) >= 2:
                recent_prices = comp_data.tail(time_window)
                
                trend = 'ثابت'
                if len(recent_prices) >= 2:
                    price_change = recent_prices['price'].iloc[-1] - recent_prices['price'].iloc[0]
                    if price_change > 0:
                        trend = 'صاعد'
                    elif price_change < 0:
                        trend = 'هابط'
                
                analysis['competitors'][competitor] = {
                    'current_price': recent_prices['price'].iloc[-1],
                    'average_price': recent_prices['price'].mean(),
                    'min_price': recent_prices['price'].min(),
                    'max_price': recent_prices['price'].max(),
                    'trend': trend,
                    'volatility': recent_prices['price'].std()
                }
        
        return analysis
    
    def seasonal_pattern_detection(self, sales_data):
        """اكتشاف الأنماط الموسمية"""
        if 'date' not in sales_data.columns or 'sales' not in sales_data.columns:
            return {'error': 'البيانات يجب أن تحتوي على أعمدة date و sales'}
        
        sales_data['date'] = pd.to_datetime(sales_data['date'])
        sales_data['month'] = sales_data['date'].dt.month
        sales_data['day_of_week'] = sales_data['date'].dt.dayofweek
        sales_data['quarter'] = sales_data['date'].dt.quarter
        
        patterns = {
            'monthly': sales_data.groupby('month')['sales'].mean().to_dict(),
            'day_of_week': sales_data.groupby('day_of_week')['sales'].mean().to_dict(),
            'quarterly': sales_data.groupby('quarter')['sales'].mean().to_dict()
        }
        
        # تحديد الأشهر الأكثر مبيعات
        monthly_sales = sales_data.groupby('month')['sales'].mean()
        peak_months = monthly_sales.nlargest(3).index.tolist()
        low_months = monthly_sales.nsmallest(3).index.tolist()
        
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        return {
            'patterns': patterns,
            'peak_months': [month_names[m] for m in peak_months],
            'low_months': [month_names[m] for m in low_months],
            'seasonality_strength': monthly_sales.std() / monthly_sales.mean()
        }
    
    def dynamic_pricing_strategy(self, current_state):
        """استراتيجية تسعير ديناميكية بناءً على الحالة الحالية"""
        strategies = []
        
        # استراتيجية بناءً على الطلب
        demand = current_state.get('demand', 0)
        capacity = current_state.get('capacity', 1)
        utilization = demand / capacity if capacity > 0 else 0
        
        if utilization > 0.9:
            strategies.append({
                'type': 'surge_pricing',
                'action': 'زيادة السعر',
                'reason': 'الطلب مرتفع جداً (>90% من الطاقة)',
                'suggested_increase': '10-20%',
                'priority': 'عالية'
            })
        elif utilization < 0.5:
            strategies.append({
                'type': 'promotional_pricing',
                'action': 'تخفيض السعر',
                'reason': 'الطلب منخفض (<50% من الطاقة)',
                'suggested_decrease': '5-15%',
                'priority': 'متوسطة'
            })
        
        # استراتيجية بناءً على المنافسين
        competitor_avg = current_state.get('competitor_avg_price', 0)
        current_price = current_state.get('current_price', 0)
        
        if current_price > 0 and competitor_avg > 0:
            price_diff = (current_price - competitor_avg) / competitor_avg
            
            if price_diff > 0.15:
                strategies.append({
                    'type': 'competitive_pricing',
                    'action': 'خفض السعر',
                    'reason': f'سعرك أعلى من المنافسين بـ {price_diff*100:.1f}%',
                    'suggested_price': competitor_avg * 1.05,
                    'priority': 'عالية'
                })
        
        # استراتيجية بناءً على الموسمية
        season_factor = current_state.get('seasonality', 1.0)
        if season_factor > 1.2:
            strategies.append({
                'type': 'seasonal_pricing',
                'action': 'زيادة السعر',
                'reason': 'موسم ذروة',
                'suggested_increase': f'{(season_factor - 1)*100:.0f}%',
                'priority': 'متوسطة'
            })
        elif season_factor < 0.8:
            strategies.append({
                'type': 'seasonal_pricing',
                'action': 'تخفيض السعر',
                'reason': 'موسم منخفض',
                'suggested_decrease': f'{(1 - season_factor)*100:.0f}%',
                'priority': 'منخفضة'
            })
        
        return {
            'strategies': strategies,
            'count': len(strategies),
            'recommended_action': strategies[0] if strategies else None
        }
    
    def generate_sample_data(self, n_samples=100):
        """توليد بيانات نموذجية للاختبار"""
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=n_samples, freq='D')
        
        data = pd.DataFrame({
            'date': dates,
            'cost': np.random.uniform(80, 120, n_samples),
            'competitor_price': np.random.uniform(150, 250, n_samples),
            'demand': np.random.randint(500, 2000, n_samples),
            'seasonality': np.random.uniform(0.8, 1.3, n_samples),
            'promotion': np.random.choice([0, 1], n_samples, p=[0.8, 0.2])
        })
        
        # توليد السعر الأمثل بناءً على العوامل
        data['optimal_price'] = (
            data['cost'] * 1.3 +
            data['competitor_price'] * 0.2 +
            data['demand'] * 0.01 +
            data['seasonality'] * 20 -
            data['promotion'] * 15
        )
        
        return data


def create_demo_predictive_ai():
    """دالة توضيحية لاستخدام نموذج AI"""
    print("=" * 70)
    print("نموذج التسعير التنبؤي بالذكاء الاصطناعي")
    print("=" * 70)
    
    # إنشاء النموذج
    ai_model = PredictivePricingAI()
    
    # توليد بيانات نموذجية
    print("\n📊 توليد بيانات تدريب نموذجية...")
    sample_data = ai_model.generate_sample_data(100)
    print(f"✅ تم توليد {len(sample_data)} عينة")
    
    # تدريب النموذج
    print("\n🤖 تدريب نموذج التعلم الآلي...")
    training_result = ai_model.integrate_machine_learning(sample_data)
    
    if 'success' in training_result:
        print(f"✅ تم التدريب بنجاح!")
        print(f"   الدقة: {training_result['accuracy']:.2%}")
        print(f"   متوسط الخطأ: {training_result['mae']:.2f} ر.س")
        print(f"   R² Score: {training_result['r2_score']:.3f}")
        
        print("\n📈 أهمية المتغيرات:")
        for feature, importance in training_result['feature_importance'].items():
            print(f"   {feature}: {importance:.3f}")
    
    # التنبؤ بسعر جديد
    print("\n🎯 التنبؤ بالسعر الأمثل...")
    current_conditions = {
        'cost': 100,
        'competitor_price': 180,
        'demand': 1500,
        'seasonality': 1.1,
        'promotion': 0
    }
    
    prediction = ai_model.predict_optimal_price(current_conditions)
    if 'predicted_price' in prediction:
        print(f"✅ السعر المتنبأ به: {prediction['predicted_price']:.2f} ر.س")
        print(f"   نطاق الثقة: {prediction['confidence_range']}")
    
    # التنبؤ بالطلب
    print("\n📊 التنبؤ بالطلب للأيام القادمة...")
    demand_forecast = ai_model.demand_forecasting(sample_data['demand'], steps=7)
    
    if 'success' in demand_forecast:
        print(f"✅ تنبؤات الطلب للأسبوع القادم:")
        for i, forecast_value in enumerate(demand_forecast['forecast'][:7], 1):
            print(f"   اليوم {i}: {forecast_value:.0f} وحدة")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    create_demo_predictive_ai()
