#!/usr/bin/env python3
"""
MedGuard Machine Learning Pipeline
Trains predictive models for overfishing risk and juvenile catch forecasting
"""

import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta
import joblib
import json

# Machine learning imports
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, r2_score, mean_squared_error

import warnings
warnings.filterwarnings('ignore')


class OverfishingRiskModel:
    """Machine learning model for overfishing risk prediction"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.trained = False
        
    def prepare_training_data(self, processed_dir='data/processed'):
        """Prepare feature matrix and labels for training"""
        print("\nPreparing training data for overfishing risk model...")
        
        processed_dir = Path(processed_dir)
        
        # Load processed data
        datasets = {}
        for file in processed_dir.glob('*.nc'):
            key = file.stem
            try:
                datasets[key] = xr.open_dataset(file)
                print(f"  ✓ Loaded {key}")
            except:
                try:
                    datasets[key] = xr.open_dataarray(file)
                    print(f"  ✓ Loaded {key}")
                except Exception as e:
                    print(f"  ✗ Error loading {key}: {e}")
        
        # Extract features
        features_list = []
        labels_list = []
        
        # Check what data is available
        if 'overfishing_risk_index' in datasets:
            risk_index = datasets['overfishing_risk_index']
            
            # Create labels (binary or multi-class)
            # High risk = 1, Low/Medium risk = 0
            labels = (risk_index > 0.6).values.flatten()
            
            # Collect features
            feature_dict = {}
            
            if 'sst_anomaly' in datasets:
                sst_anom = datasets['sst_anomaly'].isel(time=-1)
                feature_dict['sst_anomaly'] = sst_anom.values.flatten()
                
            if 'sst_standardized' in datasets:
                sst_std = datasets['sst_standardized'].isel(time=-1)
                feature_dict['sst_standardized'] = sst_std.values.flatten()
                
            if 'chl_trend' in datasets:
                chl_trend = datasets['chl_trend']
                feature_dict['chl_trend'] = chl_trend.values.flatten()
                
            if 'chl_mean' in datasets:
                chl_mean = datasets['chl_mean']
                feature_dict['chl_mean'] = chl_mean.values.flatten()
                
            if 'sst_gradient' in datasets:
                sst_grad = datasets['sst_gradient']
                feature_dict['sst_gradient'] = sst_grad.values.flatten()
                
            if 'current_speed' in datasets:
                curr_speed = datasets['current_speed'].isel(time=-1)
                feature_dict['current_speed'] = curr_speed.values.flatten()
                
            # Create DataFrame
            features_df = pd.DataFrame(feature_dict)
            self.feature_names = list(features_df.columns)
            
            # Remove NaN values
            mask = ~(features_df.isna().any(axis=1) | np.isnan(labels))
            features_clean = features_df[mask].values
            labels_clean = labels[mask]
            
            print(f"\n  Training data shape: {features_clean.shape}")
            print(f"  Number of samples: {len(features_clean)}")
            print(f"  High-risk samples: {labels_clean.sum()} ({labels_clean.mean()*100:.1f}%)")
            print(f"  Features: {', '.join(self.feature_names)}")
            
            return features_clean, labels_clean
        else:
            print("  ✗ Risk index data not found")
            return None, None
            
    def train(self, X, y):
        """Train the overfishing risk model"""
        print("\nTraining overfishing risk model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        y_pred = self.model.predict(X_test_scaled)
        
        print(f"\n  Training accuracy: {train_score:.3f}")
        print(f"  Testing accuracy: {test_score:.3f}")
        
        print("\n  Classification Report:")
        print(classification_report(y_test, y_pred, 
                                    target_names=['Low/Medium Risk', 'High Risk']))
        
        # Feature importance
        importances = self.model.feature_importances_
        feature_imp_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        print("\n  Feature Importances:")
        for idx, row in feature_imp_df.iterrows():
            print(f"    {row['feature']}: {row['importance']:.4f}")
        
        self.trained = True
        return test_score
        
    def predict_risk(self, X):
        """Predict overfishing risk probabilities"""
        if not self.trained:
            raise ValueError("Model must be trained before prediction")
        
        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict_proba(X_scaled)
        return probabilities[:, 1]  # Return probability of high risk
        
    def save_model(self, output_dir='models'):
        """Save trained model"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'trained': self.trained
        }
        
        joblib.dump(model_data, output_dir / 'overfishing_risk_model.pkl')
        print(f"\n✓ Model saved to {output_dir / 'overfishing_risk_model.pkl'}")


class JuvenileCatchForecastModel:
    """Model for forecasting juvenile fish catch events"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=150,
            max_depth=12,
            min_samples_split=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.trained = False
        
    def prepare_training_data(self, processed_dir='data/processed'):
        """Prepare data for juvenile catch forecasting"""
        print("\nPreparing training data for juvenile catch model...")
        
        processed_dir = Path(processed_dir)
        
        # Load processed data
        datasets = {}
        for file in processed_dir.glob('*.nc'):
            key = file.stem
            try:
                data = xr.open_dataset(file)
                datasets[key] = data
            except:
                try:
                    datasets[key] = xr.open_dataarray(file)
                except:
                    pass
        
        # Use juvenile habitat score as proxy for catch potential
        if 'juvenile_habitat_score' in datasets:
            target = datasets['juvenile_habitat_score'].values.flatten()
            
            # Collect features
            feature_dict = {}
            
            if 'sst_anomaly' in datasets:
                sst_anom = datasets['sst_anomaly'].isel(time=-1)
                feature_dict['sst'] = sst_anom.values.flatten()
                
            if 'chl_mean' in datasets:
                chl = datasets['chl_mean']
                feature_dict['chlorophyll'] = chl.values.flatten()
                
            if 'current_speed' in datasets:
                curr = datasets['current_speed'].isel(time=-1)
                feature_dict['current_speed'] = curr.values.flatten()
                
            # Create seasonal features
            # Simulate monthly data (in real scenario, use actual temporal data)
            month = datetime.now().month
            feature_dict['month_sin'] = np.sin(2 * np.pi * month / 12)
            feature_dict['month_cos'] = np.cos(2 * np.pi * month / 12)
            
            # Create DataFrame
            features_df = pd.DataFrame(feature_dict)
            self.feature_names = list(features_df.columns)
            
            # Remove NaN values
            mask = ~(features_df.isna().any(axis=1) | np.isnan(target))
            features_clean = features_df[mask].values
            target_clean = target[mask]
            
            print(f"\n  Training data shape: {features_clean.shape}")
            print(f"  Number of samples: {len(features_clean)}")
            print(f"  Target range: [{target_clean.min():.3f}, {target_clean.max():.3f}]")
            print(f"  Features: {', '.join(self.feature_names)}")
            
            return features_clean, target_clean
        else:
            print("  ✗ Juvenile habitat data not found")
            return None, None
            
    def train(self, X, y):
        """Train the juvenile catch forecast model"""
        print("\nTraining juvenile catch forecast model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        y_pred = self.model.predict(X_test_scaled)
        
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"\n  Training R²: {train_score:.3f}")
        print(f"  Testing R²: {test_score:.3f}")
        print(f"  RMSE: {rmse:.4f}")
        
        # Feature importance
        importances = self.model.feature_importances_
        feature_imp_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        print("\n  Feature Importances:")
        for idx, row in feature_imp_df.iterrows():
            print(f"    {row['feature']}: {row['importance']:.4f}")
        
        self.trained = True
        return test_score
        
    def forecast(self, X, days=30):
        """Forecast juvenile catch potential for next N days"""
        if not self.trained:
            raise ValueError("Model must be trained before forecasting")
        
        X_scaled = self.scaler.transform(X)
        forecast = self.model.predict(X_scaled)
        
        # Create time series (simplified - in real scenario use actual temporal prediction)
        dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
        
        return dates, forecast
        
    def save_model(self, output_dir='models'):
        """Save trained model"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'trained': self.trained
        }
        
        joblib.dump(model_data, output_dir / 'juvenile_catch_model.pkl')
        print(f"\n✓ Model saved to {output_dir / 'juvenile_catch_model.pkl'}")


class MPASimulator:
    """Simulator for MPA expansion scenarios"""
    
    def __init__(self):
        self.baseline_coverage = None
        self.scenarios = {}
        
    def load_baseline(self, processed_dir='data/processed'):
        """Load current MPA coverage"""
        print("\nLoading baseline MPA data...")
        
        processed_dir = Path(processed_dir)
        summary_file = processed_dir / 'summary_statistics.csv'
        
        if summary_file.exists():
            df = pd.read_csv(summary_file)
            if 'mpa_stats' in df.columns:
                import ast
                mpa_stats = ast.literal_eval(df['mpa_stats'].iloc[0])
                self.baseline_coverage = mpa_stats.get('coverage_percentage', 0)
                print(f"  ✓ Baseline MPA coverage: {self.baseline_coverage:.2f}%")
            else:
                self.baseline_coverage = 5.0  # Default estimate
                print(f"  ⚠ Using default baseline: {self.baseline_coverage:.2f}%")
        else:
            self.baseline_coverage = 5.0
            print(f"  ⚠ Using default baseline: {self.baseline_coverage:.2f}%")
            
    def simulate_expansion(self, expansion_pct, years=10):
        """Simulate fish stock recovery under MPA expansion"""
        print(f"\nSimulating {expansion_pct}% MPA expansion over {years} years...")
        
        new_coverage = self.baseline_coverage + expansion_pct
        
        # Simplified recovery model based on literature
        # Recovery rate typically 5-10% per year in well-managed MPAs
        base_recovery_rate = 0.07  # 7% per year
        
        # Calculate cumulative recovery
        years_array = np.arange(0, years + 1)
        
        # Logistic growth model for fish stock recovery
        K = 1.5  # Carrying capacity (150% of initial stock)
        r = base_recovery_rate * (expansion_pct / 10)  # Scale by expansion size
        
        initial_stock = 0.6  # Assume 60% of historical stock levels (overfished)
        
        stock_recovery = K / (1 + ((K - initial_stock) / initial_stock) * np.exp(-r * years_array))
        
        # Calculate biodiversity recovery (slightly slower than stock)
        biodiversity_recovery = K / (1 + ((K - initial_stock) / initial_stock) * np.exp(-r * 0.8 * years_array))
        
        # Calculate economic benefits
        # Spillover effects: increased catch in adjacent areas
        spillover_multiplier = 0.3  # 30% spillover benefit
        economic_benefit = stock_recovery * spillover_multiplier * expansion_pct * 1e6  # USD
        
        scenario = {
            'expansion_percentage': expansion_pct,
            'new_coverage': new_coverage,
            'years': years_array.tolist(),
            'stock_recovery': stock_recovery.tolist(),
            'biodiversity_recovery': biodiversity_recovery.tolist(),
            'economic_benefit_usd': economic_benefit.tolist(),
            'final_stock_level': float(stock_recovery[-1]),
            'final_biodiversity': float(biodiversity_recovery[-1])
        }
        
        self.scenarios[f'expansion_{expansion_pct}pct'] = scenario
        
        print(f"  ✓ Simulation complete")
        print(f"    New MPA coverage: {new_coverage:.2f}%")
        print(f"    Final stock recovery: {stock_recovery[-1]*100:.1f}% of historical levels")
        print(f"    Final biodiversity: {biodiversity_recovery[-1]*100:.1f}% of historical levels")
        print(f"    Estimated economic benefit (Year {years}): ${economic_benefit[-1]/1e6:.1f}M")
        
        return scenario
        
    def compare_scenarios(self, expansion_percentages=[10, 20, 30, 50]):
        """Compare multiple MPA expansion scenarios"""
        print("\nComparing MPA expansion scenarios...")
        
        results = []
        for exp_pct in expansion_percentages:
            scenario = self.simulate_expansion(exp_pct)
            results.append({
                'expansion_pct': exp_pct,
                'final_stock': scenario['final_stock_level'],
                'final_biodiversity': scenario['final_biodiversity'],
                'economic_benefit_10yr': scenario['economic_benefit_usd'][-1]
            })
        
        comparison_df = pd.DataFrame(results)
        
        print("\n  Scenario Comparison:")
        print(comparison_df.to_string(index=False))
        
        return comparison_df
        
    def save_scenarios(self, output_dir='models'):
        """Save simulation scenarios"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / 'mpa_scenarios.json', 'w') as f:
            json.dump(self.scenarios, f, indent=2)
            
        print(f"\n✓ Scenarios saved to {output_dir / 'mpa_scenarios.json'}")


def train_all_models():
    """Main function to train all models"""
    print("\n" + "="*70)
    print(" "*15 + "MEDGUARD MODEL TRAINING PIPELINE")
    print("="*70)
    print(f"Training start: {datetime.now()}")
    
    results = {}
    
    # 1. Train Overfishing Risk Model
    print("\n" + "="*70)
    print("STEP 1: OVERFISHING RISK MODEL")
    print("="*70)
    
    risk_model = OverfishingRiskModel()
    X_risk, y_risk = risk_model.prepare_training_data()
    
    if X_risk is not None and y_risk is not None:
        risk_score = risk_model.train(X_risk, y_risk)
        risk_model.save_model()
        results['risk_model_score'] = risk_score
    else:
        print("⚠ Skipping risk model training - insufficient data")
        results['risk_model_score'] = None
    
    # 2. Train Juvenile Catch Forecast Model
    print("\n" + "="*70)
    print("STEP 2: JUVENILE CATCH FORECAST MODEL")
    print("="*70)
    
    juvenile_model = JuvenileCatchForecastModel()
    X_juvenile, y_juvenile = juvenile_model.prepare_training_data()
    
    if X_juvenile is not None and y_juvenile is not None:
        juvenile_score = juvenile_model.train(X_juvenile, y_juvenile)
        juvenile_model.save_model()
        results['juvenile_model_score'] = juvenile_score
    else:
        print("⚠ Skipping juvenile model training - insufficient data")
        results['juvenile_model_score'] = None
    
    # 3. Run MPA Simulations
    print("\n" + "="*70)
    print("STEP 3: MPA EXPANSION SIMULATIONS")
    print("="*70)
    
    mpa_simulator = MPASimulator()
    mpa_simulator.load_baseline()
    comparison = mpa_simulator.compare_scenarios([10, 20, 30, 50])
    mpa_simulator.save_scenarios()
    results['mpa_scenarios'] = len(mpa_simulator.scenarios)
    
    # Save training summary
    print("\n" + "="*70)
    print("SAVING TRAINING SUMMARY")
    print("="*70)
    
    summary = {
        'training_date': datetime.now().isoformat(),
        'risk_model_accuracy': results.get('risk_model_score'),
        'juvenile_model_r2': results.get('juvenile_model_score'),
        'mpa_scenarios_created': results.get('mpa_scenarios'),
        'models_saved': ['overfishing_risk_model.pkl', 'juvenile_catch_model.pkl', 'mpa_scenarios.json']
    }
    
    output_dir = Path('models')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'training_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"✓ Training summary saved to {output_dir / 'training_summary.json'}")
    
    print("\n" + "="*70)
    print(" "*20 + "TRAINING COMPLETE!")
    print("="*70)
    print(f"Training end: {datetime.now()}")
    print(f"\nModels saved to: {output_dir.absolute()}")
    print("\nNext steps:")
    print("1. Create dashboard: python 05_create_dashboard.py")
    print("2. Test models: python test_models.py")
    print("3. Deploy to EDITO: Follow deployment guide")
    
    return results


def main():
    """Main execution"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         MEDGUARD MODEL TRAINING SYSTEM                    ║
    ║     Real-Time Overfishing Risk Monitor - Mediterranean    ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        results = train_all_models()
        return 0
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())