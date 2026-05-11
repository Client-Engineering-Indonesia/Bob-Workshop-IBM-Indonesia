"""
Model Training Module for Trade Settlement Prediction
Trains and evaluates multiple ML models
"""

import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')

# Try to import XGBoost, use GradientBoosting as fallback
XGBOOST_AVAILABLE = False
XGBClassifier = None
try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except Exception as e:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not available. Using GradientBoostingClassifier as alternative.")
    print(f"   Reason: {str(e)[:100]}")


class ModelTrainer:
    """Train and evaluate ML models for settlement prediction"""
    
    def __init__(self, X, y, test_size=0.2, random_state=42):
        self.X = X
        self.y = y
        self.test_size = test_size
        self.random_state = random_state
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        
    def train_all_models(self):
        """Train all three models"""
        print("\n" + "="*60)
        print("MODEL TRAINING")
        print("="*60)
        
        print(f"\n📊 Dataset Split:")
        print(f"   Training: {len(self.X_train)} samples ({(1-self.test_size)*100:.0f}%)")
        print(f"   Testing: {len(self.X_test)} samples ({self.test_size*100:.0f}%)")
        print(f"   Features: {self.X_train.shape[1]}")
        
        # Train Logistic Regression
        self._train_logistic_regression()
        
        # Train Random Forest
        self._train_random_forest()
        
        # Train XGBoost
        self._train_xgboost()
        
        # Select best model
        self._select_best_model()
        
        return self.results
    
    def _train_logistic_regression(self):
        """Train Logistic Regression model"""
        print("\n🔵 Training Logistic Regression...")
        
        model = LogisticRegression(
            max_iter=1000,
            random_state=self.random_state
        )
        
        model.fit(self.X_train, self.y_train)
        self.models['Logistic Regression'] = model
        
        # Evaluate
        results = self._evaluate_model(model, 'Logistic Regression')
        self.results['Logistic Regression'] = results
        
        print(f"   ✓ Accuracy: {results['accuracy']:.4f}")
        print(f"   ✓ F1-Score: {results['f1_weighted']:.4f}")
    
    def _train_random_forest(self):
        """Train Random Forest model"""
        print("\n🌲 Training Random Forest...")
        
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        model.fit(self.X_train, self.y_train)
        self.models['Random Forest'] = model
        
        # Evaluate
        results = self._evaluate_model(model, 'Random Forest')
        self.results['Random Forest'] = results
        
        print(f"   ✓ Accuracy: {results['accuracy']:.4f}")
        print(f"   ✓ F1-Score: {results['f1_weighted']:.4f}")
    
    def _train_xgboost(self):
        """Train XGBoost or GradientBoosting model"""
        if XGBOOST_AVAILABLE:
            print("\n🚀 Training XGBoost...")
            model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.random_state,
                n_jobs=-1,
                eval_metric='mlogloss'
            )
            model_name = 'XGBoost'
        else:
            print("\n🚀 Training Gradient Boosting (XGBoost alternative)...")
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=self.random_state
            )
            model_name = 'Gradient Boosting'
        
        model.fit(self.X_train, self.y_train)
        self.models[model_name] = model
        
        # Evaluate
        results = self._evaluate_model(model, model_name)
        self.results[model_name] = results
        
        print(f"   ✓ Accuracy: {results['accuracy']:.4f}")
        print(f"   ✓ F1-Score: {results['f1_weighted']:.4f}")
    
    def _evaluate_model(self, model, model_name):
        """Comprehensive model evaluation"""
        # Predictions
        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)
        
        # Metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        precision_weighted = precision_score(self.y_test, y_pred, average='weighted', zero_division=0)
        recall_weighted = recall_score(self.y_test, y_pred, average='weighted', zero_division=0)
        f1_weighted = f1_score(self.y_test, y_pred, average='weighted', zero_division=0)
        
        # Per-class metrics
        precision_per_class = precision_score(self.y_test, y_pred, average=None, zero_division=0)
        recall_per_class = recall_score(self.y_test, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(self.y_test, y_pred, average=None, zero_division=0)
        
        # Classification report
        class_report = classification_report(self.y_test, y_pred, output_dict=True, zero_division=0)
        
        # Confusion matrix
        conf_matrix = confusion_matrix(self.y_test, y_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='accuracy')
        
        # Feature importance (if available)
        feature_importance = None
        if hasattr(model, 'feature_importances_'):
            feature_importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            feature_importance = np.abs(model.coef_).mean(axis=0)
        
        results = {
            'model_name': model_name,
            'accuracy': accuracy,
            'precision_weighted': precision_weighted,
            'recall_weighted': recall_weighted,
            'f1_weighted': f1_weighted,
            'precision_per_class': precision_per_class.tolist(),
            'recall_per_class': recall_per_class.tolist(),
            'f1_per_class': f1_per_class.tolist(),
            'classification_report': class_report,
            'confusion_matrix': conf_matrix.tolist(),
            'cv_scores': cv_scores.tolist(),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance.tolist() if feature_importance is not None else None,
            'predictions': y_pred.tolist(),
            'prediction_probabilities': y_pred_proba.tolist()
        }
        
        return results
    
    def _select_best_model(self):
        """Select the best performing model"""
        print("\n" + "="*60)
        print("MODEL COMPARISON")
        print("="*60)
        
        print("\n📊 Performance Summary:")
        print(f"{'Model':<20} {'Accuracy':<12} {'F1-Score':<12} {'CV Score':<12}")
        print("-" * 60)
        
        best_score = 0
        for model_name, results in self.results.items():
            accuracy = results['accuracy']
            f1 = results['f1_weighted']
            cv_score = results['cv_mean']
            
            print(f"{model_name:<20} {accuracy:<12.4f} {f1:<12.4f} {cv_score:<12.4f}")
            
            # Select best based on F1-score
            if f1 > best_score:
                best_score = f1
                self.best_model_name = model_name
                self.best_model = self.models[model_name]
        
        print("-" * 60)
        print(f"\n🏆 Best Model: {self.best_model_name}")
        print(f"   F1-Score: {self.results[self.best_model_name]['f1_weighted']:.4f}")
        print(f"   Accuracy: {self.results[self.best_model_name]['accuracy']:.4f}")
        
        # Check if meets success criteria
        accuracy = self.results[self.best_model_name]['accuracy']
        f1_scores = self.results[self.best_model_name]['f1_per_class']
        
        print("\n✅ Success Criteria Check:")
        print(f"   Accuracy > 85%: {'✓ PASS' if accuracy > 0.85 else '✗ FAIL'} ({accuracy*100:.2f}%)")
        
        all_f1_pass = all(f1 > 0.80 for f1 in f1_scores)
        print(f"   All F1-scores > 0.80: {'✓ PASS' if all_f1_pass else '✗ FAIL'}")
        for i, f1 in enumerate(f1_scores):
            class_name = list(self.results[self.best_model_name]['classification_report'].keys())[i]
            print(f"      {class_name}: {f1:.4f}")
    
    def get_feature_importance(self, feature_names, top_n=10):
        """Get top N most important features"""
        if self.best_model is None:
            return None
        
        importance = self.results[self.best_model_name]['feature_importance']
        if importance is None:
            return None
        
        # Create dataframe
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        })
        
        # Sort and get top N
        importance_df = importance_df.sort_values('importance', ascending=False).head(top_n)
        
        return importance_df
    
    def save_model(self, model_path, metadata_path):
        """Save the best model and metadata"""
        print(f"\n💾 Saving best model...")
        
        # Save model
        joblib.dump(self.best_model, model_path)
        print(f"   ✓ Model saved to {model_path}")
        
        # Save metadata
        metadata = {
            'model_name': self.best_model_name,
            'accuracy': float(self.results[self.best_model_name]['accuracy']),
            'f1_score': float(self.results[self.best_model_name]['f1_weighted']),
            'cv_score': float(self.results[self.best_model_name]['cv_mean']),
            'training_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'n_features': self.X_train.shape[1],
            'classes': list(np.unique(self.y)),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"   ✓ Metadata saved to {metadata_path}")
    
    def save_results_report(self, output_path):
        """Save comprehensive results report to Excel"""
        print(f"\n💾 Saving results report to {output_path}...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Model comparison
            comparison_data = []
            for model_name, results in self.results.items():
                comparison_data.append({
                    'Model': model_name,
                    'Accuracy': results['accuracy'],
                    'Precision': results['precision_weighted'],
                    'Recall': results['recall_weighted'],
                    'F1-Score': results['f1_weighted'],
                    'CV Mean': results['cv_mean'],
                    'CV Std': results['cv_std'],
                    'Best Model': '✓' if model_name == self.best_model_name else ''
                })
            
            pd.DataFrame(comparison_data).to_excel(writer, sheet_name='Model Comparison', index=False)
            
            # Best model details
            best_results = self.results[self.best_model_name]
            class_report_df = pd.DataFrame(best_results['classification_report']).T
            class_report_df.to_excel(writer, sheet_name='Best Model Details')
            
            # Confusion matrix
            conf_matrix_df = pd.DataFrame(
                best_results['confusion_matrix'],
                columns=[f'Pred_{c}' for c in np.unique(self.y)],
                index=[f'True_{c}' for c in np.unique(self.y)]
            )
            conf_matrix_df.to_excel(writer, sheet_name='Confusion Matrix')
            
            # Feature importance (if available)
            if best_results['feature_importance'] is not None:
                importance_df = pd.DataFrame({
                    'Feature': [f'feature_{i}' for i in range(len(best_results['feature_importance']))],
                    'Importance': best_results['feature_importance']
                }).sort_values('Importance', ascending=False)
                importance_df.to_excel(writer, sheet_name='Feature Importance', index=False)
        
        print(f"   ✓ Results report saved successfully")


def main():
    """Test the model trainer"""
    # This would normally load from feature engineering output
    print("Model trainer module ready for integration")


if __name__ == "__main__":
    main()

# Made with Bob
