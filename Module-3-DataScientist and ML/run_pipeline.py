"""
Main ML Pipeline for Trade Settlement Prediction
Executes the complete workflow from data loading to model training
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_processing import DataProcessor
from feature_engineering import FeatureEngineer
from model_training import ModelTrainer


def main():
    """Execute the complete ML pipeline"""
    
    print("\n" + "="*70)
    print(" " * 15 + "TRADE SETTLEMENT PREDICTION")
    print(" " * 20 + "ML Pipeline Execution")
    print("="*70)
    
    start_time = datetime.now()
    
    try:
        # ============================================================
        # STEP 1: DATA PROCESSING
        # ============================================================
        print("\n" + "🔹" * 35)
        print("STEP 1: DATA PROCESSING")
        print("🔹" * 35)
        
        data_path = 'Data/xfm_trades_shaped.csv'
        processor = DataProcessor(data_path)
        
        # Load data
        df = processor.load_data()
        
        # Analyze quality
        quality_report = processor.analyze_data_quality()
        
        # Clean data
        df_clean = processor.clean_data()
        
        # Save quality report
        processor.save_quality_report('results/reports/01_data_quality_report.xlsx')
        
        print("\n✅ Step 1 Complete: Data processed and quality assessed")
        
        # ============================================================
        # STEP 2: FEATURE ENGINEERING
        # ============================================================
        print("\n" + "🔹" * 35)
        print("STEP 2: FEATURE ENGINEERING")
        print("🔹" * 35)
        
        engineer = FeatureEngineer(df_clean)
        
        # Create features
        df_engineered = engineer.create_all_features()
        
        # Prepare for modeling
        X, y, feature_cols = engineer.prepare_for_modeling()
        
        # Save feature report
        engineer.save_feature_report('results/reports/02_feature_engineering_report.xlsx')
        
        print("\n✅ Step 2 Complete: Features engineered and prepared")
        
        # ============================================================
        # STEP 3: MODEL TRAINING
        # ============================================================
        print("\n" + "🔹" * 35)
        print("STEP 3: MODEL TRAINING & EVALUATION")
        print("🔹" * 35)
        
        trainer = ModelTrainer(X, y, test_size=0.2, random_state=42)
        
        # Train all models
        results = trainer.train_all_models()
        
        # Get feature importance
        feature_importance = trainer.get_feature_importance(feature_cols, top_n=15)
        
        if feature_importance is not None:
            print("\n📊 Top 15 Most Important Features:")
            for idx, row in feature_importance.iterrows():
                print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # Save model and results
        trainer.save_model(
            'models/settlement_prediction_model.pkl',
            'models/model_metadata.json'
        )
        
        trainer.save_results_report('results/reports/03_model_results_report.xlsx')
        
        print("\n✅ Step 3 Complete: Models trained and evaluated")
        
        # ============================================================
        # PIPELINE SUMMARY
        # ============================================================
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*70)
        print("PIPELINE EXECUTION SUMMARY")
        print("="*70)
        
        print(f"\n⏱️  Execution Time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        
        print(f"\n📊 Data Statistics:")
        print(f"   Total Records: {len(df_clean):,}")
        print(f"   Features Created: {len(feature_cols)}")
        print(f"   Training Samples: {len(trainer.X_train):,}")
        print(f"   Test Samples: {len(trainer.X_test):,}")
        
        print(f"\n🏆 Best Model: {trainer.best_model_name}")
        best_results = trainer.results[trainer.best_model_name]
        print(f"   Accuracy: {best_results['accuracy']*100:.2f}%")
        print(f"   F1-Score: {best_results['f1_weighted']:.4f}")
        print(f"   CV Score: {best_results['cv_mean']:.4f} (±{best_results['cv_std']:.4f})")
        
        print(f"\n📁 Output Files Generated:")
        print(f"   ✓ results/reports/01_data_quality_report.xlsx")
        print(f"   ✓ results/reports/02_feature_engineering_report.xlsx")
        print(f"   ✓ results/reports/03_model_results_report.xlsx")
        print(f"   ✓ models/settlement_prediction_model.pkl")
        print(f"   ✓ models/model_metadata.json")
        
        print("\n" + "="*70)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print("\n📌 Next Steps:")
        print("   1. Review the Excel reports in the 'outputs/' folder")
        print("   2. Launch the Streamlit dashboard: streamlit run app.py")
        print("   3. Test predictions with sample trade data")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Pipeline execution failed!")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Made with Bob
