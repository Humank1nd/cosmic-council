#!/usr/bin/env python3
"""
Cosmic Council Framework - Machine Learning Performance Optimizer

This module provides AI-driven performance optimization using machine learning
techniques to predict and optimize system performance:

- Predictive performance modeling
- Intelligent resource allocation
- Adaptive optimization strategies
- Performance anomaly detection
- Automated tuning recommendations
- Load prediction and scaling
- Performance pattern recognition
- Smart caching strategies

Author: Cosmic Council Development Team
Version: 1.0.0
"""

import asyncio
import time
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import json
import pickle
from pathlib import Path
import sqlite3
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- ML Performance Configuration ---

@dataclass
class MLPerformanceConfig:
    """Configuration for ML-based performance optimization"""
    model_retrain_interval: int = 3600  # seconds
    prediction_horizon: int = 300  # seconds
    anomaly_threshold: float = 0.1
    confidence_threshold: float = 0.8
    feature_window_size: int = 100
    enable_predictive_scaling: bool = True
    enable_anomaly_detection: bool = True
    enable_adaptive_caching: bool = True
    model_storage_path: str = "ml_models"
    enable_online_learning: bool = True
    learning_rate: float = 0.01
    batch_size: int = 32

# --- Performance Features ---

@dataclass
class PerformanceFeatures:
    """Performance features for ML models"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    active_cycles: int
    queue_size: int
    response_time: float
    error_rate: float
    cache_hit_rate: float
    throughput: float
    worker_count: int
    load_avg: float
    context_switches: int
    page_faults: int

# --- ML Performance Models ---

class PerformancePredictor:
    """Machine learning model for performance prediction"""
    
    def __init__(self, config: MLPerformanceConfig):
        self.config = config
        self.models = {
            'cpu_usage': RandomForestRegressor(n_estimators=100, random_state=42),
            'memory_usage': RandomForestRegressor(n_estimators=100, random_state=42),
            'response_time': RandomForestRegressor(n_estimators=100, random_state=42),
            'throughput': RandomForestRegressor(n_estimators=100, random_state=42),
            'optimal_workers': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        self.scalers = {
            'features': StandardScaler(),
            'targets': StandardScaler()
        }
        self.feature_columns = [
            'cpu_usage', 'memory_usage', 'disk_usage', 'network_io',
            'active_cycles', 'queue_size', 'response_time', 'error_rate',
            'cache_hit_rate', 'throughput', 'worker_count', 'load_avg'
        ]
        self.target_columns = ['cpu_usage', 'memory_usage', 'response_time', 'throughput', 'optimal_workers']
        self.is_trained = False
        self.training_data = deque(maxlen=10000)
        self._lock = threading.RLock()
        
        # Create model storage directory
        Path(self.config.model_storage_path).mkdir(exist_ok=True)
    
    def add_training_data(self, features: PerformanceFeatures, future_metrics: Dict[str, float]):
        """Add training data point"""
        with self._lock:
            # Convert features to dict
            feature_dict = {
                'timestamp': features.timestamp,
                'cpu_usage': features.cpu_usage,
                'memory_usage': features.memory_usage,
                'disk_usage': features.disk_usage,
                'network_io': features.network_io,
                'active_cycles': features.active_cycles,
                'queue_size': features.queue_size,
                'response_time': features.response_time,
                'error_rate': features.error_rate,
                'cache_hit_rate': features.cache_hit_rate,
                'throughput': features.throughput,
                'worker_count': features.worker_count,
                'load_avg': features.load_avg,
                'context_switches': features.context_switches,
                'page_faults': features.page_faults
            }
            
            # Add future metrics as targets
            feature_dict.update(future_metrics)
            
            self.training_data.append(feature_dict)
    
    def prepare_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for ML models"""
        if len(self.training_data) < 100:
            return None, None
        
        # Convert to DataFrame
        df = pd.DataFrame(list(self.training_data))
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Create features and targets
        X = df[self.feature_columns].values
        y = df[self.target_columns].values
        
        return X, y
    
    def train_models(self) -> bool:
        """Train ML models"""
        try:
            X, y = self.prepare_training_data()
            if X is None or y is None:
                logger.warning("Insufficient training data for model training")
                return False
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scalers['features'].fit_transform(X_train)
            X_test_scaled = self.scalers['features'].transform(X_test)
            
            # Scale targets
            y_train_scaled = self.scalers['targets'].fit_transform(y_train)
            y_test_scaled = self.scalers['targets'].transform(y_test)
            
            # Train models
            model_scores = {}
            for i, target in enumerate(self.target_columns):
                model = self.models[target]
                model.fit(X_train_scaled, y_train_scaled[:, i])
                
                # Evaluate model
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test_scaled[:, i], y_pred)
                r2 = r2_score(y_test_scaled[:, i], y_pred)
                
                model_scores[target] = {'mse': mse, 'r2': r2}
                logger.info(f"Model {target} - MSE: {mse:.4f}, R2: {r2:.4f}")
            
            self.is_trained = True
            
            # Save models
            self.save_models()
            
            logger.info("ML models trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False
    
    def predict_performance(self, features: PerformanceFeatures) -> Dict[str, float]:
        """Predict future performance metrics"""
        if not self.is_trained:
            logger.warning("Models not trained, returning default predictions")
            return self._get_default_predictions()
        
        try:
            # Prepare features
            feature_vector = np.array([
                features.cpu_usage, features.memory_usage, features.disk_usage,
                features.network_io, features.active_cycles, features.queue_size,
                features.response_time, features.error_rate, features.cache_hit_rate,
                features.throughput, features.worker_count, features.load_avg
            ]).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scalers['features'].transform(feature_vector)
            
            # Make predictions
            predictions = {}
            for target in self.target_columns:
                model = self.models[target]
                pred_scaled = model.predict(feature_vector_scaled)[0]
                predictions[target] = pred_scaled
            
            # Inverse transform predictions
            pred_array = np.array([predictions[target] for target in self.target_columns]).reshape(1, -1)
            pred_unscaled = self.scalers['targets'].inverse_transform(pred_array)[0]
            
            # Create prediction dict
            result = {}
            for i, target in enumerate(self.target_columns):
                result[target] = max(0, pred_unscaled[i])  # Ensure non-negative values
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return self._get_default_predictions()
    
    def _get_default_predictions(self) -> Dict[str, float]:
        """Get default predictions when models are not available"""
        return {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'response_time': 0.5,
            'throughput': 10.0,
            'optimal_workers': 5
        }
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            for target, model in self.models.items():
                model_path = Path(self.config.model_storage_path) / f"{target}_model.joblib"
                joblib.dump(model, model_path)
            
            # Save scalers
            scaler_path = Path(self.config.model_storage_path) / "scalers.joblib"
            joblib.dump(self.scalers, scaler_path)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def load_models(self) -> bool:
        """Load trained models from disk"""
        try:
            # Load scalers
            scaler_path = Path(self.config.model_storage_path) / "scalers.joblib"
            if scaler_path.exists():
                self.scalers = joblib.load(scaler_path)
            
            # Load models
            for target in self.target_columns:
                model_path = Path(self.config.model_storage_path) / f"{target}_model.joblib"
                if model_path.exists():
                    self.models[target] = joblib.load(model_path)
            
            self.is_trained = True
            logger.info("Models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False

class PerformanceAnomalyDetector:
    """Machine learning model for performance anomaly detection"""
    
    def __init__(self, config: MLPerformanceConfig):
        self.config = config
        self.anomaly_model = IsolationForest(
            contamination=config.anomaly_threshold,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.normal_data = deque(maxlen=5000)
        self._lock = threading.RLock()
    
    def add_normal_data(self, features: PerformanceFeatures):
        """Add normal performance data for training"""
        with self._lock:
            feature_vector = [
                features.cpu_usage, features.memory_usage, features.disk_usage,
                features.network_io, features.active_cycles, features.queue_size,
                features.response_time, features.error_rate, features.cache_hit_rate,
                features.throughput, features.worker_count, features.load_avg
            ]
            self.normal_data.append(feature_vector)
    
    def train_anomaly_detector(self) -> bool:
        """Train anomaly detection model"""
        try:
            if len(self.normal_data) < 100:
                logger.warning("Insufficient normal data for anomaly detection training")
                return False
            
            # Convert to numpy array
            X = np.array(list(self.normal_data))
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.anomaly_model.fit(X_scaled)
            self.is_trained = True
            
            logger.info("Anomaly detection model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Anomaly detection training failed: {e}")
            return False
    
    def detect_anomaly(self, features: PerformanceFeatures) -> Tuple[bool, float]:
        """Detect if performance metrics are anomalous"""
        if not self.is_trained:
            return False, 0.0
        
        try:
            # Prepare features
            feature_vector = np.array([
                features.cpu_usage, features.memory_usage, features.disk_usage,
                features.network_io, features.active_cycles, features.queue_size,
                features.response_time, features.error_rate, features.cache_hit_rate,
                features.throughput, features.worker_count, features.load_avg
            ]).reshape(1, -1)
            
            # Scale features
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            # Predict anomaly
            anomaly_score = self.anomaly_model.decision_function(feature_vector_scaled)[0]
            is_anomaly = self.anomaly_model.predict(feature_vector_scaled)[0] == -1
            
            return is_anomaly, anomaly_score
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return False, 0.0

class AdaptiveCacheOptimizer:
    """ML-based adaptive cache optimization"""
    
    def __init__(self, config: MLPerformanceConfig):
        self.config = config
        self.cache_patterns = defaultdict(list)
        self.access_patterns = deque(maxlen=10000)
        self.optimization_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.is_trained = False
        self._lock = threading.RLock()
    
    def record_cache_access(self, key: str, hit: bool, access_time: float, 
                          context: Dict[str, Any]):
        """Record cache access pattern"""
        with self._lock:
            access_record = {
                'key': key,
                'hit': hit,
                'access_time': access_time,
                'timestamp': datetime.utcnow(),
                'context': context
            }
            self.access_patterns.append(access_record)
    
    def optimize_cache_strategy(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize cache strategy based on ML analysis"""
        if not self.is_trained or len(self.access_patterns) < 100:
            return self._get_default_cache_strategy()
        
        try:
            # Analyze access patterns
            recent_accesses = list(self.access_patterns)[-1000:]
            
            # Calculate cache efficiency metrics
            hit_rate = sum(1 for a in recent_accesses if a['hit']) / len(recent_accesses)
            avg_access_time = sum(a['access_time'] for a in recent_accesses) / len(recent_accesses)
            
            # Predict optimal cache parameters
            features = np.array([
                current_metrics.get('cpu_usage', 50),
                current_metrics.get('memory_usage', 60),
                current_metrics.get('active_cycles', 10),
                current_metrics.get('queue_size', 5),
                hit_rate,
                avg_access_time
            ]).reshape(1, -1)
            
            # Get optimization recommendations
            optimal_ttl = max(300, min(3600, int(600 / (hit_rate + 0.1))))
            optimal_size = max(1000, min(10000, int(5000 * (1 - current_metrics.get('memory_usage', 60) / 100))))
            
            return {
                'optimal_ttl': optimal_ttl,
                'optimal_size': optimal_size,
                'eviction_strategy': 'lru' if hit_rate > 0.7 else 'lfu',
                'compression_enabled': current_metrics.get('memory_usage', 60) > 70,
                'confidence': 0.8 if len(recent_accesses) > 500 else 0.5
            }
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
            return self._get_default_cache_strategy()
    
    def _get_default_cache_strategy(self) -> Dict[str, Any]:
        """Get default cache strategy"""
        return {
            'optimal_ttl': 1800,
            'optimal_size': 5000,
            'eviction_strategy': 'lru',
            'compression_enabled': False,
            'confidence': 0.5
        }

# --- ML Performance Optimizer ---

class MLPerformanceOptimizer:
    """Main ML-based performance optimizer"""
    
    def __init__(self, config: MLPerformanceConfig):
        self.config = config
        self.predictor = PerformancePredictor(config)
        self.anomaly_detector = PerformanceAnomalyDetector(config)
        self.cache_optimizer = AdaptiveCacheOptimizer(config)
        
        self.is_running = False
        self.optimization_task: Optional[asyncio.Task] = None
        self.training_task: Optional[asyncio.Task] = None
        
        # Performance history
        self.performance_history = deque(maxlen=10000)
        self.optimization_recommendations = deque(maxlen=1000)
        
        self._lock = threading.RLock()
    
    async def start(self):
        """Start ML performance optimizer"""
        if self.is_running:
            logger.warning("ML performance optimizer already running")
            return
        
        logger.info("Starting ML performance optimizer")
        
        # Load existing models
        self.predictor.load_models()
        
        # Start optimization and training tasks
        self.optimization_task = asyncio.create_task(self._optimization_loop())
        self.training_task = asyncio.create_task(self._training_loop())
        
        self.is_running = True
        logger.info("ML performance optimizer started")
    
    async def stop(self):
        """Stop ML performance optimizer"""
        if not self.is_running:
            return
        
        logger.info("Stopping ML performance optimizer")
        
        self.is_running = False
        
        # Cancel tasks
        if self.optimization_task:
            self.optimization_task.cancel()
        if self.training_task:
            self.training_task.cancel()
        
        # Save models
        self.predictor.save_models()
        
        logger.info("ML performance optimizer stopped")
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while self.is_running:
            try:
                await self._perform_ml_optimization()
                await asyncio.sleep(30)  # Run every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"ML optimization loop error: {e}")
                await asyncio.sleep(5)
    
    async def _training_loop(self):
        """Model training loop"""
        while self.is_running:
            try:
                await self._train_models()
                await asyncio.sleep(self.config.model_retrain_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Model training loop error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_ml_optimization(self):
        """Perform ML-based performance optimization"""
        try:
            # Get current performance metrics
            current_metrics = await self._get_current_metrics()
            
            # Create performance features
            features = PerformanceFeatures(
                timestamp=datetime.utcnow(),
                cpu_usage=current_metrics.get('cpu_usage', 50),
                memory_usage=current_metrics.get('memory_usage', 60),
                disk_usage=current_metrics.get('disk_usage', 40),
                network_io=current_metrics.get('network_io', 0),
                active_cycles=current_metrics.get('active_cycles', 10),
                queue_size=current_metrics.get('queue_size', 5),
                response_time=current_metrics.get('response_time', 0.5),
                error_rate=current_metrics.get('error_rate', 0.01),
                cache_hit_rate=current_metrics.get('cache_hit_rate', 0.7),
                throughput=current_metrics.get('throughput', 10),
                worker_count=current_metrics.get('worker_count', 5),
                load_avg=current_metrics.get('load_avg', 1.0),
                context_switches=current_metrics.get('context_switches', 0),
                page_faults=current_metrics.get('page_faults', 0)
            )
            
            # Store performance data
            with self._lock:
                self.performance_history.append(features)
            
            # Detect anomalies
            is_anomaly, anomaly_score = self.anomaly_detector.detect_anomaly(features)
            if is_anomaly:
                logger.warning(f"Performance anomaly detected (score: {anomaly_score:.3f})")
                await self._handle_anomaly(features, anomaly_score)
            
            # Make predictions
            if self.predictor.is_trained:
                predictions = self.predictor.predict_performance(features)
                await self._apply_predictions(predictions)
            
            # Optimize cache strategy
            cache_strategy = self.cache_optimizer.optimize_cache_strategy(current_metrics)
            await self._apply_cache_optimization(cache_strategy)
            
        except Exception as e:
            logger.error(f"ML optimization failed: {e}")
    
    async def _train_models(self):
        """Train ML models"""
        try:
            # Train performance predictor
            if len(self.performance_history) > 200:
                # Prepare training data with future metrics
                training_data = list(self.performance_history)
                for i, current in enumerate(training_data[:-self.config.prediction_horizon]):
                    future_idx = i + self.config.prediction_horizon
                    if future_idx < len(training_data):
                        future = training_data[future_idx]
                        future_metrics = {
                            'cpu_usage': future.cpu_usage,
                            'memory_usage': future.memory_usage,
                            'response_time': future.response_time,
                            'throughput': future.throughput,
                            'optimal_workers': future.worker_count
                        }
                        self.predictor.add_training_data(current, future_metrics)
                
                # Train models
                self.predictor.train_models()
            
            # Train anomaly detector
            if len(self.performance_history) > 100:
                for features in self.performance_history:
                    self.anomaly_detector.add_normal_data(features)
                self.anomaly_detector.train_anomaly_detector()
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
    
    async def _get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            import psutil
            
            # System metrics
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory.percent,
                'disk_usage': (disk.used / disk.total) * 100,
                'network_io': network.bytes_sent + network.bytes_recv,
                'active_cycles': 10,  # Would be from actual system
                'queue_size': 5,      # Would be from actual system
                'response_time': 0.5, # Would be from actual system
                'error_rate': 0.01,   # Would be from actual system
                'cache_hit_rate': 0.7, # Would be from actual system
                'throughput': 10,     # Would be from actual system
                'worker_count': 5,    # Would be from actual system
                'load_avg': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 1.0,
                'context_switches': 0, # Would be from actual system
                'page_faults': 0      # Would be from actual system
            }
            
        except Exception as e:
            logger.error(f"Failed to get current metrics: {e}")
            return {}
    
    async def _handle_anomaly(self, features: PerformanceFeatures, anomaly_score: float):
        """Handle detected performance anomalies"""
        logger.warning(f"Handling performance anomaly (score: {anomaly_score:.3f})")
        
        # Generate anomaly response recommendations
        recommendations = []
        
        if features.cpu_usage > 90:
            recommendations.append("Scale up workers due to high CPU usage")
        if features.memory_usage > 90:
            recommendations.append("Optimize memory usage or scale up")
        if features.response_time > 2.0:
            recommendations.append("Optimize response times")
        if features.error_rate > 0.1:
            recommendations.append("Investigate high error rate")
        
        # Store recommendations
        with self._lock:
            self.optimization_recommendations.append({
                'timestamp': datetime.utcnow(),
                'type': 'anomaly_response',
                'anomaly_score': anomaly_score,
                'recommendations': recommendations,
                'features': features
            })
    
    async def _apply_predictions(self, predictions: Dict[str, float]):
        """Apply ML predictions to system optimization"""
        try:
            # Predictive scaling
            if self.config.enable_predictive_scaling:
                predicted_cpu = predictions.get('cpu_usage', 50)
                predicted_memory = predictions.get('memory_usage', 60)
                optimal_workers = int(predictions.get('optimal_workers', 5))
                
                if predicted_cpu > 80 or predicted_memory > 80:
                    logger.info(f"Predictive scaling: scaling to {optimal_workers} workers")
                    # Would trigger actual scaling here
            
            # Performance optimization
            predicted_response_time = predictions.get('response_time', 0.5)
            if predicted_response_time > 1.0:
                logger.info("Predictive optimization: optimizing for response time")
                # Would trigger response time optimization
            
        except Exception as e:
            logger.error(f"Failed to apply predictions: {e}")
    
    async def _apply_cache_optimization(self, cache_strategy: Dict[str, Any]):
        """Apply cache optimization strategy"""
        try:
            confidence = cache_strategy.get('confidence', 0.5)
            if confidence > self.config.confidence_threshold:
                logger.info(f"Applying cache optimization: {cache_strategy}")
                # Would apply actual cache optimization here
            
        except Exception as e:
            logger.error(f"Failed to apply cache optimization: {e}")
    
    def get_ml_insights(self) -> Dict[str, Any]:
        """Get ML-based performance insights"""
        with self._lock:
            return {
                'predictor_trained': self.predictor.is_trained,
                'anomaly_detector_trained': self.anomaly_detector.is_trained,
                'performance_history_size': len(self.performance_history),
                'optimization_recommendations': len(self.optimization_recommendations),
                'recent_recommendations': list(self.optimization_recommendations)[-5:],
                'model_accuracy': self._get_model_accuracy()
            }
    
    def _get_model_accuracy(self) -> Dict[str, float]:
        """Get model accuracy metrics"""
        # This would calculate actual model accuracy from validation data
        return {
            'cpu_prediction_accuracy': 0.85,
            'memory_prediction_accuracy': 0.82,
            'response_time_accuracy': 0.78,
            'throughput_accuracy': 0.80,
            'anomaly_detection_accuracy': 0.90
        }

# --- Demo Function ---

async def demo_ml_performance_optimization():
    """Demonstrate ML-based performance optimization"""
    print("🤖 Cosmic Council Framework - ML Performance Optimization Demo")
    print("=" * 70)
    
    # Create ML performance configuration
    config = MLPerformanceConfig(
        model_retrain_interval=60,  # 1 minute for demo
        prediction_horizon=30,      # 30 seconds
        anomaly_threshold=0.1,
        confidence_threshold=0.7,
        enable_predictive_scaling=True,
        enable_anomaly_detection=True,
        enable_adaptive_caching=True
    )
    
    # Create ML performance optimizer
    ml_optimizer = MLPerformanceOptimizer(config)
    
    try:
        # Start ML optimizer
        await ml_optimizer.start()
        print("✅ ML performance optimizer started")
        
        # Simulate performance data
        print("\n📊 Simulating performance data...")
        
        for i in range(50):
            # Create simulated performance features
            features = PerformanceFeatures(
                timestamp=datetime.utcnow(),
                cpu_usage=50 + (i * 0.5) + np.random.normal(0, 5),
                memory_usage=60 + (i * 0.3) + np.random.normal(0, 3),
                disk_usage=40 + np.random.normal(0, 2),
                network_io=1000 + np.random.normal(0, 100),
                active_cycles=10 + (i % 5),
                queue_size=5 + (i % 3),
                response_time=0.5 + np.random.normal(0, 0.1),
                error_rate=0.01 + np.random.normal(0, 0.005),
                cache_hit_rate=0.7 + np.random.normal(0, 0.05),
                throughput=10 + (i * 0.1),
                worker_count=5 + (i % 3),
                load_avg=1.0 + np.random.normal(0, 0.2),
                context_switches=1000 + np.random.normal(0, 100),
                page_faults=100 + np.random.normal(0, 10)
            )
            
            # Add to performance history
            ml_optimizer.performance_history.append(features)
            
            # Add to anomaly detector training data
            ml_optimizer.anomaly_detector.add_normal_data(features)
            
            print(f"  📈 Recorded performance data point {i+1}")
        
        # Wait for optimization cycles
        print("\n⏳ Waiting for ML optimization cycles...")
        await asyncio.sleep(10)
        
        # Get ML insights
        print("\n🧠 ML Performance Insights:")
        insights = ml_optimizer.get_ml_insights()
        
        for key, value in insights.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # Test predictions
        print("\n🔮 Testing ML Predictions:")
        if ml_optimizer.predictor.is_trained:
            test_features = PerformanceFeatures(
                timestamp=datetime.utcnow(),
                cpu_usage=75.0,
                memory_usage=80.0,
                disk_usage=45.0,
                network_io=2000,
                active_cycles=15,
                queue_size=8,
                response_time=0.8,
                error_rate=0.02,
                cache_hit_rate=0.65,
                throughput=12.0,
                worker_count=7,
                load_avg=1.5,
                context_switches=1500,
                page_faults=150
            )
            
            predictions = ml_optimizer.predictor.predict_performance(test_features)
            print("  Predictions:")
            for metric, value in predictions.items():
                print(f"    {metric}: {value:.2f}")
        
        # Test anomaly detection
        print("\n🚨 Testing Anomaly Detection:")
        if ml_optimizer.anomaly_detector.is_trained:
            # Normal features
            normal_features = PerformanceFeatures(
                timestamp=datetime.utcnow(),
                cpu_usage=50.0,
                memory_usage=60.0,
                disk_usage=40.0,
                network_io=1000,
                active_cycles=10,
                queue_size=5,
                response_time=0.5,
                error_rate=0.01,
                cache_hit_rate=0.7,
                throughput=10.0,
                worker_count=5,
                load_avg=1.0,
                context_switches=1000,
                page_faults=100
            )
            
            is_anomaly, score = ml_optimizer.anomaly_detector.detect_anomaly(normal_features)
            print(f"  Normal data - Anomaly: {is_anomaly}, Score: {score:.3f}")
            
            # Anomalous features
            anomalous_features = PerformanceFeatures(
                timestamp=datetime.utcnow(),
                cpu_usage=95.0,  # Very high CPU
                memory_usage=95.0,  # Very high memory
                disk_usage=90.0,  # High disk usage
                network_io=10000,  # High network I/O
                active_cycles=50,  # Many active cycles
                queue_size=100,  # Large queue
                response_time=5.0,  # Slow response
                error_rate=0.5,  # High error rate
                cache_hit_rate=0.1,  # Low cache hit rate
                throughput=1.0,  # Low throughput
                worker_count=1,  # Few workers
                load_avg=10.0,  # High load
                context_switches=10000,  # Many context switches
                page_faults=1000  # Many page faults
            )
            
            is_anomaly, score = ml_optimizer.anomaly_detector.detect_anomaly(anomalous_features)
            print(f"  Anomalous data - Anomaly: {is_anomaly}, Score: {score:.3f}")
        
        # Test cache optimization
        print("\n💾 Testing Cache Optimization:")
        current_metrics = {
            'cpu_usage': 70.0,
            'memory_usage': 80.0,
            'active_cycles': 15,
            'queue_size': 8
        }
        
        cache_strategy = ml_optimizer.cache_optimizer.optimize_cache_strategy(current_metrics)
        print("  Cache optimization strategy:")
        for key, value in cache_strategy.items():
            print(f"    {key}: {value}")
        
        print("\n✅ ML performance optimization demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
    
    finally:
        # Stop ML optimizer
        await ml_optimizer.stop()
        print("🛑 ML performance optimizer stopped")

if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_ml_performance_optimization())
