import numpy as np
import json
from random import randint, random, uniform

class Neuron:
    def __init__(self, num_inputs, learning_rate=0.15, max_iterations=1000):
        self.weights = np.random.uniform(-0.5, 0.5, num_inputs + 1)
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations

    def tanh_taylorsversion(self, inputs):
        total = self.weights[0] + np.dot(inputs, self.weights[1:])
        tanthatthang = np.tanh(total)
        return tanthatthang

    def calculate_rmse(self, inputs, desires):
        total_sum = 0.0
        samples = len(inputs)
        
        for j in range(samples):
            actual = self.tanh_taylorsversion(inputs[j])
            error = desires[j] - actual
            total_sum += error ** 2
            
        mean_square_error = total_sum / samples
        return np.sqrt(mean_square_error)

    def train(self, inputs, desires, tolerance=0.05):
        results = {
            'rmse_history': [],
            'iterations': 0,
            'final_weights': []
        }

        for iteration in range(self.max_iterations):
            current_rmse = self.calculate_rmse(inputs, desires)
            results['rmse_history'].append(current_rmse)

            if current_rmse <= tolerance:
                results['iterations'] = iteration
                results['final_weights'] = self.weights.copy()
                return results

 
            for j in range(len(inputs)):
                actual_result = self.tanh_taylorsversion(inputs[j])
                error = desires[j] - actual_result

                if error != 0:
                    # Delta Rule: weight = weight + (learning_rate * error * input)
                    self.weights[0] += self.learning_rate * error  
                    
                    for i in range(len(inputs[j])):
                        self.weights[i + 1] += (self.learning_rate * error) * inputs[j][i]
            
            results['iterations'] = iteration + 1

        
        results['final_weights'] = self.weights.copy()
        return results

def neurontest(final_weights, test_inputs, test_desires):
    print("\n--- Here is how we test ---")
    passed = 0
    total = len(test_inputs)

    for j in range(total):
       
        z = final_weights[0] + np.dot(test_inputs[j], final_weights[1:])
        actual = np.tanh(z)
        
        result = 0
        if actual > 0.85:
            result = 1
        elif actual < -0.85:
            result = -1

        goldeneye = (result == test_desires[j])
        if goldeneye:
            passed += 1

        print(f"Computer computed: {actual: >7.4f} | Threshold Result: {result: >2} | Reality: {test_desires[j]: >2}")

    print(f"Out of {total} tests, {passed} tests were correct.")

class NeuralNetwork:
    def __init__(self, num_inputs, hidden_layers_config):
        self.layers = []
        current_input_size = num_inputs
        for num_neurons in hidden_layers_config:
            layer = [Neuron(num_inputs=current_input_size) for _ in range(num_neurons)]
            self.layers.append(layer)
            current_input_size = num_neurons
        output_layer = [Neuron(num_inputs=current_input_size)]
        self.layers.append(output_layer)

    def feedforward(self, inputs):
        current_signals = inputs
        all_layer_outputs = [] 

        for layer in self.layers:
            layer_outputs = []
            for neuron in layer:
                result = neuron.tanh_taylorsversion(current_signals)
                layer_outputs.append(result)
            all_layer_outputs.append(layer_outputs)
            current_signals = layer_outputs
        final_prediction = all_layer_outputs[-1][0]
        return final_prediction, all_layer_outputs
    def output_weights(self):
        
        for l_idx, layer in enumerate(self.layers):
            layer_name = "Output Layer" if l_idx == len(self.layers) - 1 else f"Hidden Layer {l_idx + 1}"
            print(f"\n{layer_name}:")
            for n_idx, neuron in enumerate(layer):
                print(f"  Neuron {n_idx + 1} weights: {neuron.weights}")
    def training(self, inputs, desired_output, learning_rate=0.15):

        final_prediction, all_layer_outputs = self.feedforward(inputs)
        deltas = []
        output_error = desired_output - final_prediction
        output_derivative = 1.0 - (final_prediction ** 2)
        output_delta = output_error * output_derivative
        deltas.append([output_delta])
        for l in range(len(self.layers) - 2, -1, -1):
            current_layer = self.layers[l]
            next_layer = self.layers[l + 1]
            next_layer_deltas = deltas[0]

            layer_deltas = []
            for i in range(len(current_layer)):
              
                error_signal = 0.0
                for k in range(len(next_layer)):
            
                    error_signal += next_layer[k].weights[i + 1] * next_layer_deltas[k]
              
                derivative = 1.0 - (all_layer_outputs[l][i] ** 2)
                layer_deltas.append(error_signal * derivative)
            deltas.insert(0, layer_deltas)
        for l in range(len(self.layers)):
            layer = self.layers[l]
            layer_inputs = inputs if l == 0 else all_layer_outputs[l - 1]

            for i, neuron in enumerate(layer):
                neuron.weights[0] += learning_rate * deltas[l][i]
                for j in range(len(layer_inputs)):
                    neuron.weights[j + 1] += learning_rate * deltas[l][i] * layer_inputs[j]
        
if __name__ == "__main__":
    # Data loaded
    Angels = np.load('X.npy')
    GoodBad = np.load('./backend/Y.npy')
    
    # Modified to fit constraints
    X = np.array(Angels) / 360.0 
    Y = np.array(GoodBad)

    num_features = len(X[0])
    my_network = NeuralNetwork(num_inputs=num_features, hidden_layers_config=[16,8,4,2])
    
    print(f"Initialized network expecting {num_features} inputs per sample.")
    
    total_iterations = 500
    print(f"\n--- TRAINING {total_iterations} iterations ---")
    
    # Fixed loop variables
    for iteration in range(total_iterations):
        shuffled_indices = np.random.permutation(len(X))
        X_shuffled = X[shuffled_indices]
        Y_shuffled = Y[shuffled_indices]
        for i in range(len(X)):
            sample_input = X_shuffled[i]
            desired_target = Y_shuffled[i]
            my_network.training(sample_input, desired_target, learning_rate=0.05)
            
        if (iteration + 1) % 10 == 0:
            print(f"Completed iteration {iteration + 1}/{total_iterations}")
    print("\nSaving weights to JSON for Kotlin...")
    model_data = {
        "layers": []
    }
    for layer in my_network.layers:
        layer_weights = []
        for neuron in layer:
            layer_weights.append(neuron.weights.tolist()) 
        model_data["layers"].append(layer_weights)
    with open('trained_angles_weights.json', 'w') as f:
        json.dump(model_data, f, indent=4)
        
    print("Saved as 'trained_angles_weights.json'!")
        
    print("\n--- AFTER TRAINING ---")
    passed = 0
    total = len(X)
    
    for i in range(total):
        final_result, _ = my_network.feedforward(X[i])
        
        prediction = 1 if final_result > 0 else -1 
        
        if prediction == Y[i] or (final_result > 0 and Y[i] > 0) or (final_result < 0 and Y[i] <= 0):
             passed += 1


    print(my_network.output_weights())
    print(f"Network correctly classified {passed} out of {total} samples.")
    print(f"Overall Accuracy: {(passed/total)*100:.2f}%")
