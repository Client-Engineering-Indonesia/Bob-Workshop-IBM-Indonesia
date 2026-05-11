"""
Feature Engineering Module for Trade Settlement Prediction
Creates predictive features from raw trade data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """Create and transform features for ML models"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.feature_info = {}
        self.original_features = list(df.columns)
        
    def create_all_features(self):
        """Create all engineered features"""
        print("\n" + "="*60)
        print("FEATURE ENGINEERING")
        print("="*60)
        
        print("\n🔧 Creating features...")
        
        # Time-based features
        self._create_time_features()
        
        # Price-based features
        self._create_price_features()
        
        # Categorical combinations
        self._create_categorical_features()
        
        # Risk indicators
        self._create_risk_features()
        
        # Summary
        new_features = [col for col in self.df.columns if col not in self.original_features]
        print(f"\n✓ Created {len(new_features)} new features")
        print(f"   Total features: {len(self.df.columns)}")
        
        return self.df
    
    def _create_time_features(self):
        """Create time-based features"""
        print("   • Time-based features...")
        
        # Days between trade and settlement
        self.df['days_to_settle'] = (self.df['settle_dte'] - self.df['trade_dte']).dt.days
        
        # Trade day of week (0=Monday, 6=Sunday)
        self.df['trade_day_of_week'] = self.df['trade_dte'].dt.dayofweek
        
        # Settlement day of week
        self.df['settle_day_of_week'] = self.df['settle_dte'].dt.dayofweek
        
        # Is weekend trade
        self.df['is_weekend_trade'] = (self.df['trade_day_of_week'] >= 5).astype(int)
        
        # Trade month
        self.df['trade_month'] = self.df['trade_dte'].dt.month
        
        # Settlement urgency (shorter time = higher urgency)
        self.df['settlement_urgency'] = self.df['days_to_settle'].apply(
            lambda x: 'HIGH' if x <= 1 else ('MEDIUM' if x <= 2 else 'LOW')
        )
        
        self.feature_info['time_features'] = {
            'days_to_settle': 'Number of days between trade and settlement',
            'trade_day_of_week': 'Day of week when trade occurred',
            'settle_day_of_week': 'Day of week for settlement',
            'is_weekend_trade': 'Whether trade occurred on weekend',
            'trade_month': 'Month when trade occurred',
            'settlement_urgency': 'Urgency level based on settlement timeline'
        }
    
    def _create_price_features(self):
        """Create price-based features"""
        print("   • Price-based features...")
        
        # Price categories
        price_percentiles = self.df['deal_price'].quantile([0.25, 0.5, 0.75])
        
        def categorize_price(price):
            if price <= price_percentiles[0.25]:
                return 'LOW'
            elif price <= price_percentiles[0.5]:
                return 'MEDIUM'
            elif price <= price_percentiles[0.75]:
                return 'HIGH'
            else:
                return 'VERY_HIGH'
        
        self.df['price_category'] = self.df['deal_price'].apply(categorize_price)
        
        # Price risk score (normalized)
        self.df['price_risk_score'] = (
            (self.df['deal_price'] - self.df['deal_price'].mean()) / 
            self.df['deal_price'].std()
        ).abs()
        
        # High value trade indicator
        high_value_threshold = self.df['deal_price'].quantile(0.90)
        self.df['is_high_value'] = (self.df['deal_price'] >= high_value_threshold).astype(int)
        
        self.feature_info['price_features'] = {
            'price_category': 'Categorical price range (LOW/MEDIUM/HIGH/VERY_HIGH)',
            'price_risk_score': 'Normalized price deviation from mean',
            'is_high_value': 'Whether trade is in top 10% by value'
        }
    
    def _create_categorical_features(self):
        """Create categorical combination features"""
        print("   • Categorical combination features...")
        
        # Currency-Venue combination
        self.df['currency_venue'] = self.df['currency_cd'] + '_' + self.df['trd_place']
        
        # Priority combination
        self.df['priority_combo'] = self.df['settle_priority'] + '_' + self.df['party_priority']
        
        # Message function with venue
        self.df['msg_venue'] = self.df['msg_fctn'] + '_' + self.df['trd_place']
        
        self.feature_info['categorical_features'] = {
            'currency_venue': 'Combination of currency and trading venue',
            'priority_combo': 'Combination of settlement and party priorities',
            'msg_venue': 'Combination of message function and venue'
        }
    
    def _create_risk_features(self):
        """Create risk indicator features"""
        print("   • Risk indicator features...")
        
        # Venue risk score (based on historical failure rates)
        venue_risk = {
            'EXCH': 1,  # Exchange - lowest risk
            'SECM': 2,  # Securities Market - medium risk
            'OTCO': 3,  # Over-the-counter - higher risk
            'UNKNOWN': 4  # Unknown - highest risk
        }
        self.df['venue_risk_score'] = self.df['trd_place'].map(venue_risk).fillna(4)
        
        # Currency risk (major vs minor currencies)
        major_currencies = ['USD', 'EUR', 'GBP', 'JPY']
        self.df['is_major_currency'] = self.df['currency_cd'].isin(major_currencies).astype(int)
        
        # Priority risk (LOW priority = higher risk)
        self.df['priority_risk'] = (self.df['settle_priority'] == 'LOW').astype(int)
        
        # Complex trade indicator
        self.df['is_complex_trade'] = (
            (self.df['venue_risk_score'] >= 3) & 
            (self.df['is_major_currency'] == 0)
        ).astype(int)
        
        self.feature_info['risk_features'] = {
            'venue_risk_score': 'Risk score based on trading venue (1-4)',
            'is_major_currency': 'Whether currency is major (USD/EUR/GBP/JPY)',
            'priority_risk': 'Risk indicator for low priority trades',
            'is_complex_trade': 'Indicator for complex/risky trade combinations'
        }
    
    def prepare_for_modeling(self):
        """Prepare features for ML modeling"""
        print("\n🎯 Preparing features for modeling...")
        
        # Separate features and target
        target = 'settle_status'
        
        # Features to exclude from modeling
        exclude_cols = [
            target, 'sndr_msg_id', 'settle_dte', 'trade_dte', 
            'fin_instrmnt_id'  # Unique identifier, not predictive
        ]
        
        feature_cols = [col for col in self.df.columns if col not in exclude_cols]
        
        X = self.df[feature_cols].copy()
        y = self.df[target].copy()
        
        # Encode categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns
        
        print(f"   • Encoding {len(categorical_cols)} categorical features...")
        for col in categorical_cols:
            X[col] = pd.Categorical(X[col]).codes
        
        print(f"   ✓ Features ready: {X.shape[1]} features, {X.shape[0]} samples")
        
        return X, y, feature_cols
    
    def get_feature_summary(self):
        """Get summary of all created features"""
        summary = {
            'total_features': len(self.df.columns),
            'original_features': len(self.original_features),
            'engineered_features': len(self.df.columns) - len(self.original_features),
            'feature_categories': self.feature_info
        }
        return summary
    
    def save_feature_report(self, output_path):
        """Save feature engineering report to Excel"""
        print(f"\n💾 Saving feature report to {output_path}...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Feature summary
            summary_data = []
            for category, features in self.feature_info.items():
                for feature, description in features.items():
                    summary_data.append({
                        'Category': category.replace('_', ' ').title(),
                        'Feature': feature,
                        'Description': description
                    })
            
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Feature Summary', index=False)
            
            # Feature statistics
            numeric_features = self.df.select_dtypes(include=[np.number]).columns
            stats_df = self.df[numeric_features].describe().T
            stats_df.to_excel(writer, sheet_name='Feature Statistics')
            
            # Sample with new features
            sample_cols = [col for col in self.df.columns if col not in self.original_features]
            if sample_cols:
                self.df[sample_cols].head(100).to_excel(writer, sheet_name='Sample Features', index=False)
        
        print(f"   ✓ Feature report saved successfully")


def main():
    """Test the feature engineer"""
    # Load processed data
    df = pd.read_csv('Data/xfm_trades_shaped.csv')
    df['settle_dte'] = pd.to_datetime(df['settle_dte'])
    df['trade_dte'] = pd.to_datetime(df['trade_dte'])
    
    # Create features
    engineer = FeatureEngineer(df)
    df_engineered = engineer.create_all_features()
    X, y, feature_cols = engineer.prepare_for_modeling()
    
    # Save report
    engineer.save_feature_report('results/reports/feature_engineering_report.xlsx')
    
    print("\n✅ Feature engineering complete!")
    print(f"   Features: {len(feature_cols)}")
    print(f"   Samples: {len(X)}")


if __name__ == "__main__":
    main()

# Made with Bob
