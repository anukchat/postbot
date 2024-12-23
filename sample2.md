
# Quantization Networks: A Novel Approach to Deep Neural Network Compression

## Introduction

The increasing complexity of deep neural networks (DNNs) has led to remarkable advancements in various fields. However, the high computational and memory demands of these networks pose significant challenges for their deployment on resource-constrained devices. Quantization, the process of converting full-precision neural networks into low-bitwidth integer versions, has emerged as a promising solution to address these challenges. This blog post delves into a groundbreaking paper that introduces a novel perspective on neural network quantization, formulating it as a differentiable non-linear function. This approach, termed "Quantization Networks," offers a simple, efficient, and end-to-end method for quantizing both weights and activations in DNNs.

## Main Content

The core idea behind Quantization Networks is to interpret quantization as a non-linear mapping function, similar to activation functions like Sigmoid or ReLU. Traditional quantization methods often treat it as an approximation or optimization problem, leading to issues like gradient mismatch or high computational costs. In contrast, this new approach proposes a differentiable quantization function that can be learned directly through backpropagation.

The proposed quantization function is a linear combination of several Sigmoid functions with learnable biases and scales. This formulation allows for a smooth transition from full-precision to low-bit representations during training. The key innovation lies in the use of a "temperature" parameter that controls the steepness of the Sigmoid functions. Initially, a low temperature is used to ensure the network learns effectively, and then the temperature is gradually increased to approach the ideal step function used in inference. This gradual relaxation process ensures that the network is well-trained and the gap between training and inference is minimized.

![photo from tweet](tweet_collection/media/reference_media/photo_b5eb2e6e06.jpg)

The paper highlights several advantages of this approach:

*   **Simplicity and Generality:** The method provides a straightforward and uniform solution for quantizing both weights and activations to any bit-width.
*   **End-to-End Learning:** The quantization function is differentiable, allowing for end-to-end training of the quantized network without gradient mismatch issues.
*   **State-of-the-Art Performance:** Extensive experiments on image classification (AlexNet, ResNet-18, ResNet-50) and object detection (SSD) tasks demonstrate that Quantization Networks outperform existing state-of-the-art methods.

The authors also delve into the details of training and inference with Quantization Networks. During training, the soft quantization function is used, and the temperature parameter is gradually increased. During inference, the soft quantization function is replaced with a hard step function to achieve the desired low-bit representation. The paper also includes ablation studies that explore the impact of various design choices, such as the use of non-uniform quantization, layer-wise quantization, and the temperature parameter.

The experimental results are compelling. On ImageNet classification, Quantization Networks achieve superior performance compared to other methods, especially on compact architectures like ResNet. The method also shows promising results on object detection tasks, demonstrating its versatility. The ablation studies provide valuable insights into the design choices and their impact on performance.

## Conclusion

The Quantization Networks paper presents a significant advancement in the field of neural network compression. By formulating quantization as a differentiable non-linear function, the authors have introduced a simple, efficient, and effective method for creating low-bitwidth neural networks. This approach has the potential to enable the deployment of complex DNNs on resource-constrained devices, paving the way for wider adoption of AI in various applications. The paper's clear explanations, thorough experiments, and insightful ablation studies make it a valuable contribution to the field.

## References

*   Jiwei Yang, Xu Shen, Jun Xing, Xinmei Tian, Houqiang Li, Bing Deng, Jianqiang Huang, Xiansheng Hua. Quantization Networks. https://arxiv.org/pdf/1911.09464
*   [1] Zhaowei Cai, Xiaodong He, Jian Sun, and Nuno Vasconcelos. Deep learning with low precision by half-wave gaussian quantization. In CVPR , pages 5406-5414, 2017.
*   [2] Zhangjie Cao, Mingsheng Long, Jianmin Wang, and S Yu Philip. Hashnet: Deep learning to hash by continuation. In ICCV , pages 5609-5618, 2017.
*   [3] Wenlin Chen, James Wilson, Stephen Tyree, Kilian Weinberger, and Yixin Chen. Compressing neural networks with the hashing trick. In ICML , pages 2285-2294, 2015.
*   [4] Matthieu Courbariaux, Yoshua Bengio, and Jean-Pierre David. Binaryconnect: Training deep neural networks with binary weights during propagations. In NIPS , pages 31233131, 2015.
*   [5] Abram L Friesen and Pedro Domingos. Deep learning as a mixed convex-combinatorial optimization problem. arXiv preprint arXiv:1710.11573 , 2017.
*   [6] Ian J. Goodfellow, David Warde-Farley, Mehdi Mirza, Aaron C. Courville, and Yoshua Bengio. Maxout networks. In ICML , pages 1319-1327, 2013.
*   [7] Song Han, Jeff Pool, John Tran, and William J. Dally. Learning both weights and connections for efficient neural networks. In NIPS , pages 1135-1143, 2015.
*   [8] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In CVPR , pages 770-778, 2016.
*   [9] Geoffrey Hinton, Oriol Vinyals, and Jeff Dean. Distilling the knowledge in a neural network. arXiv preprint arXiv:1503.02531 , 2015.
*   [10] Lu Hou and James T. Kwok. Loss-aware weight quantization of deep networks. In ICLR , 2018.
*   [11] Andrew G Howard, Menglong Zhu, Bo Chen, Dmitry Kalenichenko, Weijun Wang, Tobias Weyand, Marco Andreetto, and Hartwig Adam. Mobilenets: Efficient convolutional neural networks for mobile vision applications. arXiv preprint arXiv:1704.04861 , 2017.
*   [12] Yoshua Bengio Ian Goodfellow and Aaron Courville. Deep learning. Book in preparation for MIT Press, 2016.
*   [13] Forrest N Iandola, Song Han, Matthew W Moskewicz, Khalid Ashraf, William J Dally, and Kurt Keutzer. Squeezenet: Alexnet-level accuracy with 50x fewer parameters and¡ 0.5 mb model size. arXiv preprint arXiv:1602.07360 , 2016.
*   [14] Sergey Ioffe and Christian Szegedy. Batch normalization: Accelerating deep network training by reducing internal covariate shift. In ICML , pages 448-456, 2015.
*   [15] Benoit Jacob, Skirmantas Kligys, Bo Chen, Menglong Zhu, Matthew Tang, Andrew G. Howard, Hartwig Adam, and Dmitry Kalenichenko. Quantization and training of neural networks for efficient integer-arithmetic-only inference. In CVPR , pages 2704-2713, 2018.
*   [16] Max Jaderberg, Andrea Vedaldi, and Andrew Zisserman. Speeding up convolutional neural networks with low rank expansions. In BMVC , 2014.
*   [17] Joe Kilian and Hava T Siegelmann. On the power of sigmoid neural networks. In COLT , pages 137-143, 1993.
*   [18] Alex Krizhevsky, Ilya Sutskever, and Geoffrey E. Hinton. Imagenet classification with deep convolutional neural networks. In NIPS , pages 1106-1114, 2012.
*   [19] Abhisek Kundu, Kunal Banerjee, Naveen Mellempudi, Dheevatsa Mudigere, Dipankar Das, Bharat Kaul, and Pradeep Dubey. Ternary residual networks. arXiv preprint arXiv:1707.04679 , 2017.
*   [20] Cong Leng, Hao Li, Shenghuo Zhu, and Rong Jin. Extremely low bit neural network: Squeeze the last bit out with admm. In AAAI , pages 3466-3473, 2018.
*   [21] Fengfu Li and Bin Liu. Ternary weight networks. arXiv preprint arXiv:1605.04711v2 , 2016.
*   [22] Zefan Li, Bingbing Ni, Wenjun Zhang, Xiaokang Yang, and Wen Gao. Performance guaranteed network acceleration via high-order residual quantization. In ICCV , pages 26032611, 2017.
*   [23] Xiaofan Lin, Cong Zhao, and Wei Pan. Towards accurate binary convolutional neural network. In NIPS , pages 345353, 2017.
*   [24] Wei Liu, Dragomir Anguelov, Dumitru Erhan, Christian Szegedy, Scott E. Reed, Cheng-Yang Fu, and Alexander C. Berg. Ssd: Single shot multibox detector. In ECCV , pages 21-37, 2016.
*   [25] Vinod Nair and Geoffrey E. Hinton. Rectified linear units improve restricted boltzmann machines. In ICML , pages 807814, 2010.
*   [26] Michael A. Nielsen. Neural networks and deep learning. Determination Press, 2015.
*   [27] Mohammad Rastegari, Vicente Ordonez, Joseph Redmon, and Ali Farhadi. Xnor-net: Imagenet classification using binary convolutional neural networks. In ECCV , pages 525542, 2016.
*   [28] Frank Rosenblatt. The perceptron: A probabilistic model for information storage and organization in the brain. Psychological Review , pages 65-386, 1958.
*   [29] Diwen Wan, Fumin Shen, Li Liu, Fan Zhu, Jie Qin, Ling Shao, and Heng Tao Shen. Tbn: Convolutional neural network with ternary inputs and binary weights. In ECCV , pages 315-332, 2018.
*   [30] Shuang Wu, Guoqi Li, Feng Chen, and Luping Shi. Training and inference with integers in deep neural networks. In ICLR , 2018.
*   [31] Dongqing Zhang, Jiaolong Yang, Dongqiangzi Ye, and Gang Hua. Lq-nets: Learned quantization for highly accurate and compact deep neural networks. In ECCV , pages 365-382, 2018.
*   [32] Aojun Zhou, Anbang Yao, Yiwen Guo, Lin Xu, and Yurong Chen. Incremental network quantization: Towards lossless cnns with low-precision weights. In ICLR , 2017.
*   [33] Shuchang Zhou, Yuxin Wu, Zekun Ni, Xinyu Zhou, He Wen, and Yuheng Zou. Dorefa-net: Training low bitwidth convolutional neural networks with low bitwidth gradients. arXiv preprint arXiv:1606.06160 , 2016.
*   [34] Chenzhuo Zhu, Song Han, Huizi Mao, and William J. Dally. Trained ternary quantization. In ICLR , 2017.
*   [35] Bohan Zhuang, Chunhua Shen, Mingkui Tan, Lingqiao Liu, and Ian Reid. Towards effective low-bitwidth convolutional neural networks. In CVPR , pages 7920-7928, 2018.
