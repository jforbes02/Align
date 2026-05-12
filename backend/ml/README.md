# ml

This folder contains the scripts used to build and train the form-classification model. These are offline tools — you run them once to produce the trained weights file, not during normal app operation.

---

## The pipeline

```
angle_extract.py  →  X.npy + y.npy  →  machine_learning.py  →  trained_angles_weights.json
```

---

## angle_extract.py

Processes folders of reference videos and extracts joint angles from each frame to build the training dataset.

Expects two folders of videos:
- `video/correct/` — videos of good squat form (labeled `1`)
- `video/incorrect/` — videos of bad squat form (labeled `-1`)

**`video_extract(vid_path)`**
Opens a video file and runs MediaPipe on every other frame. For each frame where a pose is detected, it calculates 8 joint angles (the same 8 used at inference time) and stores them.

**`proc_folder(folder, label)`**
Runs `video_extract` on every video in a folder and stacks all the frame data together with a label.

Running this script produces:
- `X.npy` — 2D array of angle sets, one row per frame
- `y.npy` — labels, `1` or `-1` for each row

---

## machine_learning.py

Defines and trains the neural network from scratch using only NumPy — no PyTorch, no TensorFlow.

### `Neuron`
A single neuron with a tanh activation function. Trained using the **delta rule** (simple gradient descent). Has its own `train()` and `calculate_rmse()` methods but these are only used in the single-neuron prototype — the full network uses `NeuralNetwork` instead.

### `NeuralNetwork`
A multi-layer network built from `Neuron` objects.

**`feedforward(inputs)`**
Passes inputs through every layer in sequence. Each neuron applies tanh to a weighted sum of its inputs. Returns the final output and all intermediate layer outputs (needed for backprop).

**`training(inputs, desired_output)`**
One training step using **backpropagation**:
1. Run feedforward to get a prediction
2. Calculate the error at the output
3. Propagate that error backwards through each layer (chain rule)
4. Update every weight slightly in the direction that reduces error

Running the script trains on `X.npy` / `y.npy` for 500 epochs and saves the result:

---

## trained_angles_weights.json

The output of training. Contains all the learned weights for every neuron in every layer, serialized to JSON so `scores/scoring.py` can load and use them at runtime without needing any ML framework.

---

## X.npy / y.npy

The training data — joint angles and their form labels. Re-generate these by running `angle_extract.py` if you add new training videos.
