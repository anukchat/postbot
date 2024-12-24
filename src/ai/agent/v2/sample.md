# Quantization Networks: Deploying Large Neural Networks on Resource-Constrained Devices

The deployment of large neural networks on resource-constrained devices presents a significant challenge due to the substantial computational and memory requirements of these models. Traditional floating-point representations of weights and activations demand considerable resources, hindering their practical application in edge computing and mobile environments. Quantization offers a compelling solution by reducing the precision of numerical representations, thereby decreasing model size and accelerating inference. Quantization Networks, which employ low-precision integer representations, achieve this by mapping floating-point values to a discrete set of integers. This approach yields substantial benefits, including reduced memory footprint, faster computation due to simpler integer arithmetic, and lower power consumption, making it feasible to deploy sophisticated deep learning models on devices with limited resources.


## Quantization as a Non-Linear Function

The core innovation of Quantization Networks lies in reformulating the quantization operation as a differentiable non-linear function. This approach draws inspiration from activation functions commonly used in deep neural networks, such as Sigmoid, ReLU, and Maxout. Instead of treating quantization as a discrete approximation or optimization problem, it is viewed as a continuous, learnable transformation. This perspective enables end-to-end training of quantized networks, addressing the gradient mismatch issues prevalent in approximation-based methods.

The ideal low-bit quantization function is conceptualized as a combination of several unit step functions with specific biases and scales. This can be expressed as:

```
y =  ∑ (sᵢ * A(βx - bᵢ)) - o
```

where:
-   `x` represents the full-precision weight or activation to be quantized.
-   `y` is the quantized integer value, constrained to a predefined set `Y`.
-   `A` is the unit step function.
-   `β` is a scale factor for the input.
-   `sᵢ` and `bᵢ` are the scales and biases for the unit step functions, respectively.
-   `o` is a global offset to keep the quantized output zero-centered.

However, the unit step function is not differentiable, making it unsuitable for gradient-based learning. To overcome this, the unit step functions are replaced with Sigmoid functions, resulting in a "soft" quantization function. This allows the quantization operation to be differentiable, enabling backpropagation and end-to-end learning.

To further refine the training process and bridge the gap between the soft quantization function (used during training) and the ideal step function (used during inference), a temperature parameter `T` is introduced into the Sigmoid function:

```
σ(Tx) = 1 / (1 + exp(-Tx))
```

A larger `T` makes the Sigmoid function more closely resemble a step function. During training, `T` is gradually increased, starting from a small value to ensure effective learning, and then increasing over training epochs to approach the ideal step function for inference. This gradual increase allows the network to be well-trained, while also minimizing the difference between training and inference quantization functions.

The complete soft quantization function used during training is defined as:

```
y_d = Q(x_d) = α * (∑ (sᵢ * σ(T(βx_d - bᵢ))) - o)
```

where:

-   `x_d` is the full-precision input value.
-   `y_d` is the quantized output.
-   `α` is the output scale factor.
-   `β` is the input scale factor.
-   `bᵢ` are the learnable biases.
-   `T` is the temperature parameter.
-   `σ` is the Sigmoid function.

During inference, the Sigmoid function is replaced by the unit step function:

```
y = α * (∑ (sᵢ * A(βx - bᵢ)) - o)
```

This transformation ensures that the network operates with discrete integer values during deployment, while still benefiting from the smooth, differentiable training process. The parameters α, β, and b are learned during training, allowing the network to adapt the quantization function to the specific characteristics of the weights and activations being quantized.


## 3.2. Training and Inference with Quantization Networks

Inspired by the advantage of sigmoid units against the perceptron in feedforward networks, we propose replacing the unit step functions in the ideal quantization function Eq. (5) with sigmoid functions. With this replacement, we can have a differentiable quantization function, termed soft quantization function, as shown in Fig. 2(c). Thus, we can learn any low-bit quantized neural networks in an end-toend manner based on back propagation.

However, the ideal quantization function Eq. (5) is applied in the inference stage. The use of different quantization functions in training and inference stages may decrease the performance of DNNs. To narrow the gap between the ideal quantization function used in inference stage and the soft quantization function used in training stage, we introduce a temperature *T* to the sigmoid function, motivated by the temperature introduced in distilling [9],

σ ( *Tx* ) = 1 / (1 + exp ( -*Tx* )).

With a larger *T*, the gap between two quantization functions is smaller, but the learning capacity of the quantization networks is lower since the gradients of the soft quantization function will be zero in more cases. To solve this problem, in the training stage we start with a small *T* to ensure the quantized networks can be well learned, and then gradually increase *T* w.r.t. the training epochs. In this way, the quantized networks can be well learned and the gap between two quantization functions will be very small at the end of the training.

**Forward Propagation**. In detail, for a set of full-precision weights or activations to be quantized *X* = {*x<sub>d</sub>*, *d* = 1, · · · , *D*}, the quantization function is applied to each *x<sub>d</sub>* independently:

*y<sub>d</sub>* = *Q*(*x<sub>d</sub>*) = α (∑<sub>*i*=1</sub><sup>*n*</sup> *s<sub>i</sub>* σ ( *T* (β*x<sub>d</sub>* - *b<sub>i</sub>*)) - *o*),

where β and α are the scale factors of the input and output respectively. *b* = [*b<sub>i</sub>*, *i* = 1, · · · , *n*], where *b<sub>i</sub>* indicates the beginning of the input for the *i*-th quantization interval except the first quantization interval, and the beginning of the first quantization interval is -∞. The temperature *T* controls the gap between the ideal quantization function and the soft quantization function. The gradual change from no quantization to complete quantization along with the adjustment of *T* is depicted in Fig. 2.

The quantization function Eq. (7) is applied to every full-precision value *x* that need to be quantized, just as applying ReLU in traditional DNNs. *x* can be either a weight or an activation in DNNs. The output *y* replaces *x* for further computing.

**Backward Propagation**. During training stage, we need to back propagate the gradients of loss ℒ through the quantization function, as well as compute the gradients with respect to the involved parameters:

∂ℒ/∂*x<sub>d</sub>* = ∂ℒ/∂*y<sub>d</sub>* · ∑<sub>*i*=1</sub><sup>*n*</sup> *T*βα*s<sub>i</sub>* *g<sub>id</sub>* (α*s<sub>i</sub>* - *g<sub>id</sub>*),

∂ℒ/∂α = ∑<sub>*d*=1</sub><sup>*D*</sup> ∂ℒ/∂*y<sub>d</sub>* · (1/α)*y<sub>d</sub>*,

∂ℒ/∂β = ∑<sub>*d*=1</sub><sup>*D*</sup> ∂ℒ/∂*y<sub>d</sub>* · ∑<sub>*i*=1</sub><sup>*n*</sup> *T* *x<sub>d</sub>* α*s<sub>i</sub>* *g<sub>id</sub>* (α*s<sub>i</sub>* - *g<sub>id</sub>*),

∂ℒ/∂*b<sub>i</sub>* = ∑<sub>*d*=1</sub><sup>*D*</sup> ∂ℒ/∂*y<sub>d</sub>* · -*T* α*s<sub>i</sub>* *g<sub>id</sub>* (α*s<sub>i</sub>* - *g<sub>id</sub>*).

where *g<sub>id</sub>* = σ ( *T* (β*x<sub>d</sub>* - *b<sub>i</sub>*)). We do not need to compute the gradients of *n*, *s<sub>i</sub>* and offset *o*, because they are directly obtained by *Y*. Our soft quantization function is a differentiable transformation that introduces quantized weights and activations into the network.

**Training and Inference**. To quantize a network, we specify a set of weights or activations and insert the quantization function for each of them, according to Eq. (7). Any layer that previously received *x* as an input, now receives *Q*(*x*). Any module that previously used *W* as parameters, now uses *Q*(*W*). The smooth quantization function *Q* allows efficient training for networks, but it is neither necessary nor desirable during inference; we want the specified weights or activations to be discrete numbers. For this, once the network has been trained, we replace the sigmoid function in Eq. (7) by the unit step function for quantization:

*y* = α (∑<sub>*i*=1</sub><sup>*n*</sup> *s<sub>i</sub>* *A* (β*x* - *b<sub>i</sub>*) - *o*).

Algorithm 1 summarizes the procedure for training quantization networks. For a full-precision network *N* with *M* modules, where a module can be either a convolutional layer or a fully connected layer, we denote all the activations to be quantized in the *m*-th module as *X<sup>(m)</sup>*, and denote all the weights to be quantized in the *m*-th module as Θ<sup>(*m*)</sup>. All elements in *X<sup>(m)</sup>* share the same quantization function parameters {α<sup>(*m*)</sup><sub>*X*</sub>, β<sup>(*m*)</sup><sub>*X*</sub>, *b<sup>(m)</sup><sub>X</sub>*}. All elements in Θ<sup>(*m*)</sup> share the same quantization function parameters {α<sup>(*m*)</sup><sub>Θ</sub>, β<sup>(*m*)</sup><sub>Θ</sub>, *b<sup>(m)</sup><sub>Θ</sub>*}. We apply the quantization function module by module. Then, we train the network with gradually increased temperature *T*.

```
Algorithm 1 Training quantization networks

Input: Network N with M modules M m =1 and their corresponding activations/inputs {X ( m ) } M m =1 and trainable weights (or other parameters) { Θ ( m ) } M m =1

Output: Quantized network for inference, N inf Q

N tr Q ← N // Training quantization network

for epoch ← 1 to Max Epochs do

  for m ← 1 to M do

    Apply the soft quantization function to each element x m d in X ( m ) and each element θ m d in Θ ( m ) :

      y m d = Q { α ( m ) X ,β ( m ) X ,β ( m ) Θ } ( x m d ) ,

      ̂ θ m d = Q { α ( m ) Θ ,β ( m ) Θ ,b ( m ) Θ } ( θ m d ) .

    Forward propagate module m with the quantized weights and activations.

  end for

end for

Train N tr Q to optimize the parameters Θ ∪ { α ( m ) Θ , β ( m ) Θ , b ( m ) Θ , α ( m ) X , β ( m ) X , b ( m ) X } M m =1 with gradually increased temperature T

N inf Q ← N tr Q // Inference quantization network with frozen parameters

for m ← 1 to M do

  Replace the soft quantization functions with Eq. (12) for inference.

end for
```


## Conclusion

In summary, Quantization Networks offer a compelling approach to reduce the computational and memory footprint of deep learning models. By representing weights and activations with lower bit precision, these networks enable faster inference and deployment on resource-constrained devices. The techniques, as explored in research such as [https://arxiv.org/pdf/1911.09464], demonstrate the potential for significant efficiency gains without substantial compromise in accuracy. Further research and experimentation in this area will be crucial for realizing the full potential of quantized models in real-world applications. We encourage readers to explore the cited paper and delve deeper into the practical implementation of these techniques.
