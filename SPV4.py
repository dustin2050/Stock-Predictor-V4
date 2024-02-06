import argparse


def install_dependencies():
    import os
    import subprocess
    import time
    import urllib.request
    import tarfile
    import sys

    def download_file(url, filename):
        print(f"Downloading {filename}...")
        start_time = time.time()
        response = urllib.request.urlopen(url)
        file_size = int(response.headers["Content-Length"])
        downloaded = 0
        block_size = 8192
        with open(filename, "wb") as file:
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                file.write(buffer)
                downloaded += len(buffer)
                progress = downloaded / file_size * 100
                print(f"Progress: {progress:.2f}%", end="\r")
        print()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Download complete: {filename} (Time: {elapsed_time:.2f} seconds)")

    def extract_tar_gz(filename):
        print(f"Extracting {filename}...")
        start_time = time.time()
        with tarfile.open(filename, "r:gz") as tar:
            file_count = len(tar.getmembers())
            extracted = 0
            for member in tar:
                tar.extract(member)
                extracted += 1
                progress = extracted / file_count * 100
                print(f"Progress: {progress:.2f}%", end="\r")
        print()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Extraction complete: {filename} (Time: {elapsed_time:.2f} seconds)")

    def install_ta_lib():
        print("Installing TA-Lib...")
        start_time = time.time()
        os.chdir("ta-lib")
        subprocess.run(["./configure", "--prefix=/usr"], check=True)
        subprocess.run(
            ["make", "-s"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["sudo", "make", "-s", "install"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        os.chdir("..")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"TA-Lib installation complete (Time: {elapsed_time:.2f} seconds)")

    def install_dependencies():
        print("Installing Python dependencies...")
        start_time = time.time()
        packages = [
            "pandas",
            "numpy",
            "scikit-learn",
            "tensorflow",
            "matplotlib",
            "ta-lib",
            "bayesian-optimization",
        ]
        total_packages = len(packages)
        progress = 0
        for package in packages:
            progress += 1
            print(f"Installing {package}... ({progress}/{total_packages})")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", package], check=True
            )
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(
            f"Python dependencies installation complete (Time: {elapsed_time:.2f} seconds)"
        )

    if __name__ == "__main__":
        print("Welcome to the SPV4 installation!")
        print("This script will install all the necessary dependencies.\n")

        time.sleep(2)

        download_file(
            "https://deac-fra.dl.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz",
            "ta-lib-0.4.0-src.tar.gz",
        )

        print("Extraction process will begin shortly...")
        print("Please wait while the files are being extracted.")

        extract_tar_gz("ta-lib-0.4.0-src.tar.gz")

        print("Extraction process completed successfully!\n")
        print("TA-Lib installation will now begin.")

        install_ta_lib()

        print("TA-Lib installation completed successfully!\n")

        print("Python dependencies installation will now begin.")

        install_dependencies()

        print("Python dependencies installation completed successfully!\n")
        print("SPV4 installation completed successfully!")


def prepare_data():
    print("Preprocessing and preparing the CSV data...")
    import os
    import pandas as pd
    import talib
    import matplotlib.pyplot as plt

    # List all CSV files in the "data" folder
    data_folder = "data"
    csv_files = [file for file in os.listdir(data_folder) if file.endswith(".csv")]

    # Print the available CSV files with numbers for selection
    print("Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i + 1}. {file}")

    # Ask for user input to select a CSV file
    selected_file_index = (
        int(input("Enter the number of the CSV file to preprocess: ")) - 1
    )
    selected_file = csv_files[selected_file_index]
    selected_file_path = os.path.join(data_folder, selected_file)

    # Preprocess the selected CSV file
    df = pd.read_csv(selected_file_path)


    # Stelle sicher, dass alle Werte in den relevanten Spalten numerisch sind
    columns_to_check = ['Close', 'Open', 'High', 'Low']
    for column in columns_to_check:
      df[column] = pd.to_numeric(df[column], errors='coerce')

    # Exportiere die DataFrame in eine neue CSV-Datei mit einer Mindestanzahl von Dezimalstellen
    df.to_csv(selected_file_path, index=False, float_format='%.6f')

    # CSV Datei neu einlesen
    df = pd.read_csv(selected_file_path)


    df["SMA"] = talib.SMA(df["Close"], timeperiod=14).round(decimals=5)
    df["RSI"] = talib.RSI(df["Close"], timeperiod=14)
    df["MACD"], _, _ = talib.MACD(
        df["Close"], fastperiod=12, slowperiod=26, signalperiod=9
    )
    df["upper_band"], df["middle_band"], df["lower_band"] = talib.BBANDS(
        df["Close"], timeperiod=20
    )
    df["aroon_up"], df["aroon_down"] = talib.AROON(df["High"], df["Low"], timeperiod=25)
    df["kicking"] = talib.CDLKICKINGBYLENGTH(
        df["Open"], df["High"], df["Low"], df["Close"]
    )

    df["ATR"] = talib.ATR(df["High"], df["Low"], df["Close"], timeperiod=14)
    df["upper_band_supertrend"] = df["High"] - (df["ATR"] * 2)
    df["lower_band_supertrend"] = df["Low"] + (df["ATR"] * 2)
    df["in_uptrend"] = df["Close"] > df["lower_band_supertrend"]
    df["supertrend_signal"] = df["in_uptrend"].diff().fillna(0)

    df["ROC"] = talib.ROC(df["Close"], timeperiod=14)

    # Replace "False" with 0 and "True" with 1
    df = df.replace({False: 0, True: 1})

    # Fill missing values with 0
    df.fillna(0, inplace=True)

    # Concatenate the columns in the order you want
    df2 = pd.concat(
        [
            df["Date"],
            df["Close"],
            df["Open"],
            #df["Adj Close"],
            #df["Volume"],
            df["High"],
            df["Low"],
            df["SMA"],
            df["MACD"],
            df["upper_band"],
            df["middle_band"],
            df["lower_band"],
            df["supertrend_signal"],
            df["RSI"],
            df["aroon_up"],
            df["aroon_down"],
            df["kicking"],
            df["ATR"],
            df["upper_band_supertrend"],
            df["lower_band_supertrend"],
            df["ROC"],
        ],
        axis=1,
    )

    # Save the DataFrame to a new CSV file with indicators
    df2.to_csv("data.csv", index=False, float_format='%.6f')

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    ax1.plot(df["Close"], label="Close")
    ax1.plot(df["SMA"], label="SMA")
    ax1.fill_between(
        df.index, df["upper_band"], df["lower_band"], alpha=0.2, color="gray"
    )
    ax1.plot(df["upper_band"], linestyle="dashed", color="gray")
    ax1.plot(df["middle_band"], linestyle="dashed", color="gray")
    ax1.plot(df["lower_band"], linestyle="dashed", color="gray")
    ax1.scatter(
        df.index[df["supertrend_signal"] == 1],
        df["Close"][df["supertrend_signal"] == 1],
        marker="^",
        color="green",
        s=100,
    )
    ax1.scatter(
        df.index[df["supertrend_signal"] == -1],
        df["Close"][df["supertrend_signal"] == -1],
        marker="v",
        color="red",
        s=100,
    )
    ax1.legend()

    ax2.plot(df["RSI"], label="RSI")
    ax2.plot(df["aroon_up"], label="Aroon Up")
    ax2.plot(df["aroon_down"], label="Aroon Down")
    ax2.scatter(
        df.index[df["kicking"] == 100],
        df["High"][df["kicking"] == 100],
        marker="^",
        color="green",
        s=100,
    )
    ax2.scatter(
        df.index[df["kicking"] == -100],
        df["Low"][df["kicking"] == -100],
        marker="v",
        color="red",
        s=100,
    )
    ax2.legend()

    plt.xlim(df.index[0], df.index[-1])

    plt.show()


def train_model():
    print("Training the SPV4 model...")
    import os
    import sys

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import (
        LSTM,
        Dense,
        BatchNormalization,
        GRU,
        Conv1D,
        MaxPooling1D,
        TimeDistributed,
    )
    from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
    from sklearn.metrics import mean_absolute_percentage_error, r2_score

    print("TensorFlow version:", tf.__version__)

    # Define reward function
    def get_reward(y_true, y_pred):
        mape = mean_absolute_percentage_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        reward = ((1 - mape) + r2) / 2
        return reward

    # Load data
    data = pd.read_csv("data.csv")

    # Normalize data
    scaler = MinMaxScaler()
    data_norm = scaler.fit_transform(
        data[
            [
                "Close",
                "Open",
                #"Adj Close",
                #"Volume",
                "High",
                "Low",
                "SMA",
                "MACD",
                "upper_band",
                "middle_band",
                "lower_band",
                "supertrend_signal",
                "RSI",
                "aroon_up",
                "aroon_down",
                "kicking",
                "upper_band_supertrend",
                "lower_band_supertrend",
                "ROC",
            ]
        ]
    )

    # Split data into train and test sets
    train_data_norm = data_norm[: int(0.8 * len(data))]
    test_data_norm = data_norm[int(0.8 * len(data)) :]

    # Define time steps
    timesteps = 48

    # Create sequences of timesteps
    def create_sequences(data, timesteps):
        X = []
        y = []
        for i in range(timesteps, len(data)):
            X.append(data[i - timesteps : i])
            y.append(data[i, 0])
        return np.array(X), np.array(y)

    X_train, y_train = create_sequences(train_data_norm, timesteps)
    X_test, y_test = create_sequences(test_data_norm, timesteps)

    # Define the Deep RL model
    def create_model(units, filters, kernel_size, learning_rate):
        model = Sequential()
        model.add(Conv1D(filters=filters, kernel_size=kernel_size, activation="relu"))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Conv1D(filters=filters // 2, kernel_size=kernel_size // 2, activation="relu"))
        model.add(LSTM(units=units, return_sequences=True, input_shape=(timesteps, X_train.shape[2])))
        model.add(BatchNormalization())
        model.add(GRU(units=units, return_sequences=True))
        model.add(BatchNormalization())
        model.add(Dense(units=units))
        model.add(BatchNormalization())
        model.add(TimeDistributed(Dense(units=units)))
        model.add(BatchNormalization())
        model.add(LSTM(units=units // 2, return_sequences=True))
        model.add(BatchNormalization())
        model.add(GRU(units=units // 2, return_sequences=True))
        model.add(BatchNormalization())
        model.add(TimeDistributed(Dense(units=units // 2)))
        model.add(BatchNormalization())
        model.add(LSTM(units=units // 4))
        model.add(BatchNormalization())
        model.add(Dense(units=1))

        # Define the RL optimizer and compile the model
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        model.compile(optimizer=optimizer, loss="mse")

        return model

    # Define Bayesian optimization
    from bayes_opt import BayesianOptimization

    # Define RL training loop
    epochs = 5
    batch_size = 256
    best_reward = None
    best_model_path = "model.keras"
    min_reward_threshold = float(input("Enter the minimum reward threshold (e.g., 0.7): "))

    def optimize_model(units, filters, kernel_size, learning_rate):
        model = create_model(int(units), int(filters), int(kernel_size), learning_rate)

        # Train the model for one epoch
        for i in range(0, len(X_train), batch_size):
            if i == 0:
                print("Batch", i, "/", len(X_train))
            else:
                sys.stdout.write('\033[F\033[K')
                print("Batch", i, "/", len(X_train))
            batch_X = X_train[i:i + batch_size]
            batch_y = y_train[i:i + batch_size]
            history = model.fit(batch_X, batch_y, batch_size=batch_size, epochs=1, verbose=1)
            sys.stdout.write('\033[F\033[K')

        # Evaluate the model on the test set
        print("\nEvaluating the Model\n")
        y_pred_test = model.predict(X_test)
        sys.stdout.write('\033[F\033[K')
        test_reward = get_reward(y_test, y_pred_test)
        test_loss = model.evaluate(X_test, y_test, verbose=0)
        sys.stdout.write('\033[F\033[K')

        print("Test reward:", test_reward)
        print("Test loss:", test_loss)

        return test_reward

    # Define the search space boundaries
    pbounds = {
        'units': (50, 800),
        'filters': (50, 800),
        'kernel_size': (2, 15),
        'learning_rate': (0.0001, 0.015),
    }

    # Define Bayesian optimization function
    optimizer = BayesianOptimization(f=optimize_model, pbounds=pbounds)

    # Perform Bayesian optimization
    num_iterations = 10

    for _ in range(num_iterations):
        optimizer.maximize(init_points=2, n_iter=3)
        best_params = optimizer.max['params']
        best_reward = optimizer.max['target']

        print("Best reward:", best_reward)
        print("Best parameters:", best_params)

        # Check if the minimum reward threshold is reached
        if best_reward >= min_reward_threshold:
            break

    print("Training completed.")

    # Load the best model and evaluate it
    model = create_model(int(best_params['units']), int(best_params['filters']), int(best_params['kernel_size']), best_params['learning_rate'])
    model.fit(X_train, y_train, batch_size=batch_size, epochs=epochs, verbose=1)
    model.save("model.keras")

    y_pred_test = model.predict(X_test)
    test_reward = get_reward(y_test, y_pred_test)
    test_loss = model.evaluate(X_test, y_test)

    print("Final test reward:", test_reward)
    print("Final test loss:", test_loss)

def evaluate_model():
    print("Evaluating the model...")
    import os

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

    import pandas as pd
    import numpy as np
    import tensorflow as tf
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
    import matplotlib.pyplot as plt

    print("TensorFlow version:", tf.__version__)

    # Load data
    data = pd.read_csv("data.csv")

    # Split data into train and test sets
    train_data = data.iloc[: int(0.8 * len(data))]
    test_data = data.iloc[int(0.8 * len(data)) :]

    # Normalize data
    scaler = MinMaxScaler()
    train_data_norm = scaler.fit_transform(
        train_data[
            [
                "Close",
                "Open",
               # "Adj Close",
               # "Volume",
                "High",
                "Low",
                "SMA",
                "MACD",
                "upper_band",
                "middle_band",
                "lower_band",
                "supertrend_signal",
                "RSI",
                "aroon_up",
                "aroon_down",
                "kicking",
                "upper_band_supertrend",
                "lower_band_supertrend",
                "ROC",
            ]
        ]
    )
    test_data_norm = scaler.transform(
        test_data[
            [
                "Close",
                "Open",
                #"Adj Close",
                #"Volume",
                "High",
                "Low",
                "SMA",
                "MACD",
                "upper_band",
                "middle_band",
                "lower_band",
                "supertrend_signal",
                "RSI",
                "aroon_up",
                "aroon_down",
                "kicking",
                "upper_band_supertrend",
                "lower_band_supertrend",
                "ROC",
            ]
        ]
    )

    # Define time steps
    timesteps = 48

    def create_sequences(data, timesteps):
        X = []
        y = []
        for i in range(timesteps, len(data)):
            X.append(data[i - timesteps : i])
            y.append(data[i, 0])
        return np.array(X), np.array(y)

    # Load model
    model = load_model("model.keras")

    # Evaluate model
    rmse_scores = []
    mape_scores = []
    rewards = []
    for i in range(10):
        model = load_model("model.keras")
        print(f"Evaluating model {i+1}/10")
        X_test, y_test = create_sequences(test_data_norm, timesteps)
        print(X_test.shape)        
        y_pred = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = mean_absolute_percentage_error(y_test, y_pred)
        rmse_scores.append(rmse)
        mape_scores.append(mape)
        if mape < 0.05:
            rewards.append(1 - mape)
            model.save("model.keras")
        else:
            rewards.append(0.3 - mape)

    # Print results
    print(f"Mean RMSE: {np.mean(rmse_scores)}")
    print(f"Mean MAPE: {np.mean(mape_scores)}")
    print(f"Total Rewards: {sum(rewards)}")

    # Plot results
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))
    axs[0].plot(rmse_scores)
    axs[0].set_title("RMSE")
    axs[1].plot(mape_scores)
    axs[1].set_title("MAPE Score")
    axs[2].plot(rewards)
    axs[2].set_title("Rewards")
    plt.tight_layout()
    plt.show()



def fine_tune_model():
    import os
    import sys
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    from sklearn.preprocessing import MaxAbsScaler
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_percentage_error
    from tensorflow.keras.models import load_model

    # Set the logging level to only log errors
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    print("Finetuning the model...")
    print("TensorFlow version:", tf.__version__)

    def get_reward(y_true, y_pred):
      mape = mean_absolute_percentage_error(y_true, y_pred)
      r2 = r2_score(y_true, y_pred)
      reward = (((1 - mape) * 0.1) + (r2 * 1.9)) / 2
      return reward

    def create_sequences(data, timesteps):
      X, y = [], []
      for i in range(timesteps, len(data)):
        X.append(data[i - timesteps: i])
        y.append(data[i, 0])
      return np.array(X), np.array(y)

    # Load data
    data = pd.read_csv("data.csv")

    # Split data into train, validation, and test sets
    train_size = int(0.7 * len(data))
    validation_size = int(0.15 * len(data))

    train_data = data.iloc[:train_size]
    validation_data = data.iloc[train_size: train_size + validation_size]
    test_data = data.iloc[train_size + validation_size:]

    # Feature columns
    feature_columns = [
                "Close",
                "Open",
                #"Adj Close",
                #"Volume",
                "High",
                "Low",
                "SMA",
                "MACD",
                "upper_band",
                "middle_band",
                "lower_band",
                "supertrend_signal",
                "RSI",
                "aroon_up",
                "aroon_down",
                "kicking",
                "upper_band_supertrend",
                "lower_band_supertrend",
                "ROC",
    ]

    # Normalize data
    scaler = MaxAbsScaler()
    scaler.fit(train_data[feature_columns])  # Fit only to the training data

    train_data_norm = scaler.transform(train_data[feature_columns])
    validation_data_norm = scaler.transform(validation_data[feature_columns])
    test_data_norm = scaler.transform(test_data[feature_columns])

    # Define time steps
    timesteps = 48
    X_train, y_train = create_sequences(train_data_norm, timesteps)
    X_validation, y_validation = create_sequences(validation_data_norm, timesteps)
    X_test, y_test = create_sequences(test_data_norm, timesteps)

    # Ask for the reward threshold
    reward_threshold = float(input("Enter the reward threshold (0 - 1, 0.9 recommended): "))

    # Initialize the best validation reward and counter for early stopping
    best_val_reward = -np.inf
    no_improvement_count = 0
    early_stopping_patience = 5

    # Load the model
    model = load_model("model.keras")

    # Training loop
    epochs = 50
    batch_size = 32

    for epoch in range(epochs):
        print(f"Epoch {epoch + 1} / {epochs}")
        history = model.fit(
            X_train, y_train,
            batch_size=batch_size,
            epochs=1,
            validation_data=(X_validation, y_validation)
        )

        # Evaluate the model on the validation set
        val_pred = model.predict(X_validation)
        val_reward = get_reward(y_validation, val_pred)

        print(f"Validation reward for epoch {epoch + 1}: {val_reward}")

        # If the current reward is better than the best one, save the model
        if val_reward > best_val_reward:
            print(f"Validation reward improved from {best_val_reward:.4f} to {val_reward:.4f}, saving model")
            best_val_reward = val_reward
            model.save("model.keras")
            no_improvement_count = 0  # Reset counter when improvement occurs
        else:
            no_improvement_count += 1
            print(f"No improvement in validation reward for {no_improvement_count} consecutive epoch(s).")

        # Early stopping condition
        if no_improvement_count >= early_stopping_patience:
            print(f"Stopping early due to no improvement in validation reward for {early_stopping_patience} consecutive epochs.")
            break

        if val_reward >= reward_threshold:
            print(f"Reward threshold of {reward_threshold} reached on validation set.")
            break

    print("Finetuning completed.")




def predict_future_data():
    print("Utilizing the model for predicting future data (30 days)...")
    import os

    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import MinMaxScaler
    from tensorflow.keras.models import load_model
    import matplotlib.pyplot as plt

    # Load data
    data = pd.read_csv("data.csv")

    # Normalize data
    scaler = MinMaxScaler()
    data_norm = scaler.fit_transform(
        data[
            [
                "Close",
                "Open",
               # "Adj Close",
               # "Volume",
                "High",
                "Low",
                "SMA",
                "MACD",
                "upper_band",
                "middle_band",
                "lower_band",
                "supertrend_signal",
                "RSI",
                "aroon_up",
                "aroon_down",
                "kicking",
                "upper_band_supertrend",
                "lower_band_supertrend",
                "ROC",
            ]
        ]
    )

    # Define time steps
    timesteps = 48

    # Create sequences of timesteps
    def create_sequences(data, timesteps):
        X = []
        for i in range(timesteps, len(data)):
            X.append(data[i - timesteps : i])
        return np.array(X)

    X_data = create_sequences(data_norm, timesteps)

    # Load model
    model = load_model("model.keras")
    model.summary()

    num_predictions = 500

    # Make predictions for next num_predictions Minutes
    X_pred = X_data[-num_predictions:].reshape(
        (num_predictions, timesteps, X_data.shape[2])
    )
    y_pred = model.predict(X_pred)[:, 0]

    # Inverse transform predictions
    y_pred = scaler.inverse_transform(
        np.hstack(
            [
                np.zeros((len(y_pred), data_norm.shape[1] - 1)),
                np.array(y_pred).reshape(-1, 1),
            ]
        )
    )[:, -1]

    # Generate date index for predictions
    last_date = data["Date"].iloc[-1]
    index = pd.date_range(
        last_date, periods=num_predictions, freq="H", tz="UTC"
    ).tz_localize(None)

    # Calculate % change
    y_pred_pct_change = (y_pred - y_pred[0]) / y_pred[0] * 100

    # Save predictions and % change in a CSV file
    predictions = pd.DataFrame(
        {"Date": index, "Predicted Close": y_pred, "% Change": y_pred_pct_change}
    )
    predictions.to_csv("predictions.csv", index=False)

    print(predictions)

"""
    # Calculate % change
    y_pred_pct_change = (y_pred - y_pred[0]) / y_pred[0] * 100

    # Save predictions and % change in a CSV file
    predictions = pd.DataFrame(
        {"Date": index, "Predicted Close": y_pred, "% Change": y_pred_pct_change}
    )
    predictions.to_csv("predictions.csv", index=False)

    print(predictions)

    # Find the rows with the lowest and highest predicted close and the highest and lowest % change
    min_close_row = predictions.iloc[predictions["Predicted Close"].idxmin()]
    max_close_row = predictions.iloc[predictions["Predicted Close"].idxmax()]
    max_pct_change_row = predictions.iloc[predictions["% Change"].idxmax()]
    min_pct_change_row = predictions.iloc[predictions["% Change"].idxmin()]

    # Print the rows with the lowest and highest predicted close and the highest and lowest % change
    print(f"\n\nHighest predicted close:\n{max_close_row}\n")
    print(f"Lowest predicted close:\n{min_close_row}\n")
    print(f"Highest % change:\n{max_pct_change_row}\n")
    print(f"Lowest % change:\n{min_pct_change_row}")

    # Plot historical data and predictions
    plt.plot(data["Close"].values, label="Actual Data")
    plt.plot(
        np.arange(len(data), len(data) + num_predictions),
        y_pred,
        label="Predicted Data",
    )

    # Add red and green arrows for highest and lowest predicted close respectively, and highest and lowest percentage change
    plt.annotate(
        "↓",
        xy=(min_close_row.name - len(data), min_close_row["Predicted Close"]),
        color="red",
        fontsize=16,
        arrowprops=dict(facecolor="red", shrink=0.05),
    )
    plt.annotate(
        "↑",
        xy=(max_close_row.name - len(data), max_close_row["Predicted Close"]),
        color="green",
        fontsize=16,
        arrowprops=dict(facecolor="green", shrink=0.05),
    )
    plt.annotate(
        "↑",
        xy=(max_pct_change_row.name - len(data), y_pred.max()),
        color="green",
        fontsize=16,
        arrowprops=dict(facecolor="green", shrink=0.05),
    )
    plt.annotate(
        "↓",
        xy=(min_pct_change_row.name - len(data), y_pred.min()),
        color="red",
        fontsize=16,
        arrowprops=dict(facecolor="red", shrink=0.05),
    )

    # Add legend and title
    plt.legend()
    plt.title("Predicted Close Prices")

    # Show plot
    plt.show()
"""

def compare_predictions():
    print("Comparing the predictions with the actual data...")
    import os
    import pandas as pd
    import matplotlib.pyplot as plt

    # Get a list of CSV files in the "data" folder
    data_folder = "data"
    csv_files = [file for file in os.listdir(data_folder) if file.endswith(".csv")]

    # Display the list of CSV files to the user
    print("Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i + 1}. {file}")

    # Ask the user to select a CSV file
    selected_file = None
    while selected_file is None:
        try:
            file_number = int(
                input(
                    "Enter the number corresponding to the CSV file you want to select: "
                )
            )
            if file_number < 1 or file_number > len(csv_files):
                raise ValueError()
            selected_file = csv_files[file_number - 1]
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Load predicted and actual data
    predicted_data = pd.read_csv("predictions.csv")
    actual_data = pd.read_csv(os.path.join(data_folder, selected_file))

    # Rename columns for clarity
    predicted_data = predicted_data.rename(columns={"Predicted Close": "Close"})
    actual_data = actual_data.rename(columns={"Close": "Actual Close"})

    # Join predicted and actual data on the date column
    combined_data = pd.merge(predicted_data, actual_data, on="Date")

    # Calculate the absolute percentage error between the predicted and actual values
    combined_data["Absolute % Error"] = (
        abs(combined_data["Close"] - combined_data["Actual Close"])
        / combined_data["Actual Close"]
        * 100
    )

    # Calculate the mean absolute percentage error and print it
    mape = combined_data["Absolute % Error"].mean()
    print(f"Mean Absolute Percentage Error: {mape:.2f}%")

    # Find the row with the highest and lowest absolute percentage error and print them
    min_error_row = combined_data.iloc[combined_data["Absolute % Error"].idxmin()]
    max_error_row = combined_data.iloc[combined_data["Absolute % Error"].idxmax()]
    print(f"\nMost Accurate Prediction:\n{min_error_row}\n")
    print(f"Least Accurate Prediction:\n{max_error_row}\n")

    # Plot the predicted and actual close prices
    plt.plot(combined_data["Date"], combined_data["Close"], label="Predicted Close")
    plt.plot(combined_data["Date"], combined_data["Actual Close"], label="Actual Close")

    # Add title and legend
    plt.title("Predicted vs Actual Close Prices")
    plt.legend()

    # Show plot
    plt.show()


def gen_stock():
    print("Generating Stock Data...")
    import csv
    import random
    import datetime

    def generate_stock_data_csv(file_path, num_lines, data_type):
        # Define the column names
        columns = ["Date", "Close", "Adj Close", "Volume", "High", "Low", "Open"]

        # Generate stock data based on the selected data type
        data = []
        start_date = datetime.datetime(2022, 1, 1)
        for i in range(num_lines):
            if data_type == "linear":
                close_price = 100.0 + i * 10
            elif data_type == "exponential":
                close_price = 100.0 * (1.1**i)
            elif data_type == "random":
                if i > 0:
                    prev_close = data[i - 1][1]
                    close_price = prev_close * random.uniform(0.95, 1.05)
                else:
                    close_price = 100.0
            elif data_type == "trend":
                if i > 0:
                    prev_close = data[i - 1][1]
                    close_price = prev_close + random.uniform(-2, 2)
                else:
                    close_price = 100.0
            else:
                raise ValueError("Invalid data type provided.")

            date = start_date + datetime.timedelta(days=i)
            adj_close = close_price
            volume = random.randint(100000, 1000000)
            high = close_price * random.uniform(1.01, 1.05)
            low = close_price * random.uniform(0.95, 0.99)
            open_price = close_price * random.uniform(0.98, 1.02)

            data.append(
                [
                    date.strftime("%Y-%m-%d"),
                    close_price,
                    adj_close,
                    volume,
                    high,
                    low,
                    open_price,
                ]
            )

        # Save the generated data to a CSV file
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(data)

        print(f"Stock data CSV file '{file_path}' generated successfully.")

    # Prompt the user for options
    num_lines = int(input("Enter the number of lines: "))
    data_type = input("Enter the data type (linear/exponential/random/trend): ")
    file_path = "data/example.csv"

    # Generate the stock data CSV file
    generate_stock_data_csv(file_path, num_lines, data_type)


def do_all_actions():
    prepare_data()
    train_model()
    evaluate_model()
    fine_tune_model()
    evaluate_model()
    predict_future_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SPV4 Script")
    parser.add_argument(
        "--install", action="store_true", help="Install all dependencies for SPV4"
    )
    parser.add_argument(
        "--generate_stock", action="store_true", help="Generate Stock Data"
    )
    parser.add_argument(
        "--prepare_data",
        action="store_true",
        help="Preprocess and Prepare the CSV Data",
    )
    parser.add_argument("--train", action="store_true", help="Train the SPV4 Model")
    parser.add_argument("--eval", action="store_true", help="Evaluate the Model")
    parser.add_argument("--fine_tune", action="store_true", help="Finetune the Model")
    parser.add_argument(
        "--predict",
        action="store_true",
        help="Utilize the Model for Predicting Future Data (30 Days)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare the Predictions with the Actual Data",
    )
    parser.add_argument(
        "--do-all",
        action="store_true",
        help="Do all actions from above (No Install & Generating Stock Data)",
    )

    args = parser.parse_args()

    if args.do_all:
        do_all_actions()
    else:
        if args.install:
            install_dependencies()
        if args.generate_stock:
            gen_stock()
        if args.prepare_data:
            prepare_data()
        if args.train:
            train_model()
        if args.eval:
            evaluate_model()
        if args.fine_tune:
            fine_tune_model()
        if args.predict:
            predict_future_data()
        if args.compare:
            compare_predictions()
