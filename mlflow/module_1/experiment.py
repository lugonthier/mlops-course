import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


mlflow.set_tracking_uri("http://127.0.0.1:5000") 
mlflow.set_experiment("Iris Classification Basics")

iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

feature_names = iris.feature_names
X_train_df = pd.DataFrame(X_train, columns=feature_names)
X_test_df = pd.DataFrame(X_test, columns=feature_names)


params = {
    "C": 1.2, 
    "solver": "liblinear",
    "random_state": 42
}

with mlflow.start_run(run_name="Iris_Logistic_Regression_C1") as run:
    print(f"MLflow Run ID: {run.info.run_id}")

    mlflow.log_params(params)
    print("Parameters logged.")

    model = LogisticRegression(**params)
    model.fit(X_train_df, y_train)
    print("Model trained.")

    y_pred = model.predict(X_test_df)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')

    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1_score", f1)
    print(f"Metrics logged: accuracy={accuracy:.4f}, f1_score={f1:.4f}")
    input_example = X_train_df.head()
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="logistic_regression_model",
        input_example=input_example,
        registered_model_name="IrisClassifier" 
    )
    print("Model logged.")

    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=iris.target_names, yticklabels=iris.target_names)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    
    plot_path = "confusion_matrix.png"
    plt.savefig(plot_path)
    print(f"Confusion matrix plot saved to {plot_path}")
    
    mlflow.log_artifact(plot_path)
    print("Confusion matrix plot logged as artifact.")
    
    plt.close()

    if os.path.exists(plot_path):
        os.remove(plot_path)
        print(f"Removed local plot file: {plot_path}")

print("MLflow run completed.")
print(f"To view the UI, run 'mlflow ui' in the '{os.getcwd()}' directory and navigate to http://127.0.0.1:5000") 