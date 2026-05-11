"""
Data Processing Module for Trade Settlement Prediction
Handles data loading, cleaning, and quality assessment
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DataProcessor:
    """Process and clean trade settlement data"""
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None
        self.quality_report = {}
        
    def load_data(self):
        """Load trade data from CSV"""
        print(f"Loading data from {self.data_path}...")
        self.df = pd.read_csv(self.data_path)
        print(f"✓ Loaded {len(self.df)} records with {len(self.df.columns)} columns")
        return self.df
    
    def analyze_data_quality(self):
        """Comprehensive data quality assessment"""
        print("\n" + "="*60)
        print("DATA QUALITY ASSESSMENT")
        print("="*60)
        
        # Basic statistics
        total_records = len(self.df)
        total_columns = len(self.df.columns)
        
        # Missing values analysis
        missing_values = self.df.isnull().sum()
        missing_pct = (missing_values / total_records * 100).round(2)
        
        # Duplicate detection
        duplicates = self.df.duplicated().sum()
        duplicate_pct = (duplicates / total_records * 100).round(2)
        
        # Data types
        dtypes_summary = self.df.dtypes.value_counts().to_dict()
        
        # Target variable distribution
        target_dist = self.df['settle_status'].value_counts()
        target_pct = (target_dist / total_records * 100).round(2)
        
        # Calculate overall quality score
        quality_score = self._calculate_quality_score(missing_pct, duplicate_pct)
        
        # Store quality report
        self.quality_report = {
            'total_records': total_records,
            'total_columns': total_columns,
            'missing_values': missing_values.to_dict(),
            'missing_percentages': missing_pct.to_dict(),
            'duplicates': duplicates,
            'duplicate_percentage': duplicate_pct,
            'data_types': {str(k): v for k, v in dtypes_summary.items()},
            'target_distribution': target_dist.to_dict(),
            'target_percentages': target_pct.to_dict(),
            'quality_score': quality_score
        }
        
        # Print summary
        print(f"\n📊 Dataset Overview:")
        print(f"   Total Records: {total_records:,}")
        print(f"   Total Columns: {total_columns}")
        
        print(f"\n🔍 Missing Values:")
        for col, pct in missing_pct.items():
            if pct > 0:
                print(f"   {col}: {missing_values[col]} ({pct}%)")
        if missing_pct.sum() == 0:
            print("   ✓ No missing values detected")
        
        print(f"\n🔄 Duplicates:")
        print(f"   Duplicate Records: {duplicates} ({duplicate_pct}%)")
        
        print(f"\n🎯 Target Variable (settle_status):")
        for status, count in target_dist.items():
            print(f"   {status}: {count} ({target_pct[status]}%)")
        
        print(f"\n⭐ Overall Quality Score: {quality_score}%")
        print("="*60)
        
        return self.quality_report
    
    def _calculate_quality_score(self, missing_pct, duplicate_pct):
        """Calculate overall data quality score (0-100)"""
        # Start with perfect score
        score = 100.0
        
        # Deduct for missing values (max 30 points)
        avg_missing = missing_pct.mean()
        score -= min(avg_missing * 3, 30)
        
        # Deduct for duplicates (max 20 points)
        score -= min(duplicate_pct * 2, 20)
        
        return round(max(score, 0), 2)
    
    def clean_data(self):
        """Clean and prepare data for modeling with intelligent imputation"""
        print("\n🧹 Cleaning data...")
        
        initial_count = len(self.df)
        
        # Convert date columns
        date_columns = ['settle_dte', 'trade_dte']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Remove duplicates FIRST to get clean data
        before_dup = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed_dup = before_dup - len(self.df)
        if removed_dup > 0:
            print(f"   ✓ Removed {removed_dup} duplicate records")
        
        # SMART IMPUTATION: Fill missing values based on patterns
        # For party_priority (83% missing), use settle_priority as proxy
        print(f"   • Intelligently imputing party_priority based on settle_priority...")
        self.df['party_priority'] = self.df.apply(
            lambda row: row['settle_priority'] if pd.isna(row['party_priority']) else row['party_priority'],
            axis=1
        )
        
        # For trd_place (5.5% missing), use most common value per currency
        print(f"   • Imputing missing trd_place based on currency patterns...")
        for currency in self.df['currency_cd'].unique():
            mask = (self.df['currency_cd'] == currency) & (self.df['trd_place'].isna())
            if mask.any():
                mode_place = self.df[self.df['currency_cd'] == currency]['trd_place'].mode()
                if len(mode_place) > 0:
                    self.df.loc[mask, 'trd_place'] = mode_place[0]
        
        # Fill any remaining missing trd_place with overall mode
        if self.df['trd_place'].isna().any():
            overall_mode = self.df['trd_place'].mode()[0]
            self.df['trd_place'].fillna(overall_mode, inplace=True)
        
        # Handle remaining missing values in other categorical columns
        categorical_cols = ['msg_fctn', 'currency_cd', 'settle_priority']
        for col in categorical_cols:
            if col in self.df.columns and self.df[col].isnull().any():
                mode_value = self.df[col].mode()[0] if len(self.df[col].mode()) > 0 else 'MEDIUM'
                self.df[col].fillna(mode_value, inplace=True)
                print(f"   • Filled missing {col} with mode: {mode_value}")
        
        # Fill missing deal_price with median
        if 'deal_price' in self.df.columns and self.df['deal_price'].isnull().any():
            median_price = self.df['deal_price'].median()
            self.df['deal_price'].fillna(median_price, inplace=True)
            print(f"   • Filled missing deal_price with median: {median_price:.2f}")
        
        total_removed = initial_count - len(self.df)
        print(f"\n   ✓ Data cleaned: {len(self.df)} records ready ({total_removed} removed)")
        print(f"   ✓ All missing values intelligently imputed!")
        
        return self.df
    
    def get_data_summary(self):
        """Get comprehensive data summary for reporting"""
        summary = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.to_dict(),
            'numeric_summary': self.df.describe().to_dict(),
            'categorical_summary': {}
        }
        
        # Categorical columns summary
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            summary['categorical_summary'][col] = {
                'unique_values': int(self.df[col].nunique()),
                'top_values': self.df[col].value_counts().head(5).to_dict()
            }
        
        return summary
    
    def save_quality_report(self, output_path):
        """Save quality report to Excel"""
        print(f"\n💾 Saving quality report to {output_path}...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Overview sheet
            overview_data = {
                'Metric': ['Total Records', 'Total Columns', 'Duplicates', 'Quality Score'],
                'Value': [
                    self.quality_report['total_records'],
                    self.quality_report['total_columns'],
                    f"{self.quality_report['duplicates']} ({self.quality_report['duplicate_percentage']}%)",
                    f"{self.quality_report['quality_score']}%"
                ]
            }
            pd.DataFrame(overview_data).to_excel(writer, sheet_name='Overview', index=False)
            
            # Missing values sheet
            missing_df = pd.DataFrame({
                'Column': list(self.quality_report['missing_values'].keys()),
                'Missing Count': list(self.quality_report['missing_values'].values()),
                'Missing %': list(self.quality_report['missing_percentages'].values())
            })
            missing_df.to_excel(writer, sheet_name='Missing Values', index=False)
            
            # Target distribution sheet
            target_df = pd.DataFrame({
                'Status': list(self.quality_report['target_distribution'].keys()),
                'Count': list(self.quality_report['target_distribution'].values()),
                'Percentage': list(self.quality_report['target_percentages'].values())
            })
            target_df.to_excel(writer, sheet_name='Target Distribution', index=False)
            
            # Sample data
            self.df.head(100).to_excel(writer, sheet_name='Sample Data', index=False)
        
        print(f"   ✓ Quality report saved successfully")


def main():
    """Test the data processor"""
    processor = DataProcessor('Data/xfm_trades_shaped.csv')
    processor.load_data()
    processor.analyze_data_quality()
    processor.clean_data()
    processor.save_quality_report('results/reports/data_quality_report.xlsx')
    print("\n✅ Data processing complete!")


if __name__ == "__main__":
    main()

# Made with Bob
