# TORCS AI Driver

[TORCS](http://torcs.sourceforge.net/index.php) controller of team "JesusTakeTheWheel".

## Requirements

* TensorFlow
* keyboard (for optional manual data collection)

A `requirements.txt` for pip is provided.

## Models

* **Multi-Layer Perceptron** with 3-layers with 150 hidden units each by default
* **Recurrent Neural Network** with 3-layers with 150 hidden units and sequences of length 5 each by default
* **Extreme Learning Machine** with a hidden layer of size 400

All models train using simple SGD or AdaGrad with a learning rate of 0.01.

Training drive data can be used to train the models using their respective training scripts:

```
$ python3 train/mlp.py input.csv output_path
$ python3 train/rnn.py input.csv output_path
$ python3 train/elm.py input.csv output_path
```

Optionally, the number of training parameters can be specified:

```
$ python3 train/mlp.py --iterations 200000 input.csv output_path
$ python3 train/rnn.py --iterations 200000 input.csv output_path
$ python3 train/elm.py --iterations 200000 input.csv output_path
```

The output folder will contain the fully trained TensorFlow model and can be loaded into the corresponding drivers.

## Drivers

### Jesus

The superclass for autonomous drivers. Driving commands are processed by the underlying "Holy Coast" ML-model.

* **Default Drive** behaviour uses commands from the currently engaged "Holy Coast" model 
* **Overtake Drive** is used during overtaking and avoidance procesures of surrounding opponents
* **Recovery Drive** is used if the default controller is deemed to be stuck
* **Cheesy Drive** is engaged during opponent obstruction and "Cheesus" mode

### Judas

Controller which drives down center track with a maximum speed of 80 km/h. While neither fast nor very intelligent, it collects very clean training data.

### Manual

A manually controlled driver which collects sensor and command data for training autonomous models. Drive using `WASD`, press `L` to add data into save buffer and press `J` to clear buffer of recorded states. To record keypresses, this driver needs to be run as a superuser.

### MLP, RNN, ELM

Autonomous driver using either an MLP, RNN or ELM as the underlying model.

Place any pre-trained models into the respective directories `resources/models/mlp/`, `resources/models/rnn/` or `resources/models/elm/`. Setting Symlinks at these locations may help with the swift interchange of models.

### Gear

The gear driver's special use case is the evolutionary optimization of up and downshift RPM parameters. Obtain these numbers by running a couple of generations and plug in the numbers into the Jesus driver.

## Run

To start the default client simply run the start script:

```
$ ./start.sh
```

Optionally, a port the client should connect to can be specified (3001 is the default):

```
$ ./start.sh -p 3002
```

To run any specific driver, use the scipts located in `run/` e.g.:

```
$ python3 run/mlp.py
$ python3 run/rnn.py
$ python3 run/elm.py
```

---

Christina, David and Max wish you successful autonomous racing!
