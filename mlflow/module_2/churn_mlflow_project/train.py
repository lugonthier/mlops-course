import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow
import mlflow.sklearn

def main():
    parser = argparse.ArgumentParser(description="Train a classifier on the Iris dataset.")
    parser.add_argument("--C", type=float, default=1.0, help="Inverse of regularization strength for Logistic Regression.")
    parser.add_argument("--n_estimators", type=int, default=100, help="Number of trees in the forest for RandomForest.")
    parser.add_argument("--max_depth", type=int, default=2, help="Maximum depth of the tree for RandomForest.")
    parser.add_argument("--model_type", type=str, default="logistic", choices=["logistic", "randomforest"], help="Type of model to train (logistic or randomforest).")
    parser.add_argument("--data_path", type=str, required=True, help="Path to the dataset.")
    parser.add_argument("--test_size", type=float, default=0.2, help="Proportion of the dataset to include in the test split.")
    parser.add_argument("--random_state", type=int, default=42, help="Random seed for reproducibility.")

    args = parser.parse_args()
    #mlflow.set_tracking_uri("./mlruns")
    with mlflow.start_run():
        mlflow.log_param("C", args.C)
        mlflow.log_param("n_estimators", args.n_estimators)
        mlflow.log_param("max_depth", args.max_depth)
        mlflow.log_param("model_type", args.model_type)
        mlflow.log_param("test_size", args.test_size)
        mlflow.log_param("random_state", args.random_state)

        try:
            iris_df = pd.read_csv(args.data_path)
        except FileNotFoundError:
            print(f"Error: Data file not found at {args.data_path}")
            mlflow.log_metric("load_data_success", 0)
            return
        except Exception as e:
            print(f"Error loading data: {e}")
            mlflow.log_metric("load_data_success", 0)
            return
        
        mlflow.log_metric("load_data_success", 1)

        X = iris_df.drop(columns=['Churn'])
        y = iris_df['Churn']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=args.test_size, random_state=args.random_state
        )

        if args.model_type == "logistic":
            model = LogisticRegression(C=args.C, random_state=args.random_state, max_iter=200)
            mlflow.log_param("solver", model.solver)
        elif args.model_type == "randomforest":
            model = RandomForestClassifier(
                n_estimators=args.n_estimators, 
                max_depth=args.max_depth, 
                random_state=args.random_state
            )
        else:
            print(f"Unsupported model type: {args.model_type}")
            return

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision_weighted", precision)
        mlflow.log_metric("recall_weighted", recall)
        mlflow.log_metric("f1_weighted", f1)

        mlflow.sklearn.log_model(model, "model")
        print(f"Model trained: {args.model_type}")
        print(f"Accuracy: {accuracy:.4f}")

if __name__ == "__main__":
    main() 