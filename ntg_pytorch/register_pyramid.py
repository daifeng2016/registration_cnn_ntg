import cv2
import scipy.misc as smi
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F

def compute_pyramid_while(image_batch,f,nL,ration,use_cuda=False):
    image_batch = image_batch.transpose(1, 2).transpose(2, 3)   # batch,h,w,channel
    if use_cuda:
        image_batch = image_batch.cpu().numpy()
    else:
        image_batch = image_batch.numpy()
    multi_level_image_batch = []
    multi_level_image_batch.append(torch.from_numpy(image_batch.transpose((0,3,1,2))))
    for level in range(1,nL):

        level_image_batch = []
        for image_item in image_batch:
            level_image = smi.imresize(image_item[:, :, 0], size=ration) / 255.0
            if len(level_image.shape) == 2:
                level_image = level_image[:,:,np.newaxis]

            level_image_batch.append(level_image)

        image_batch = np.copy(level_image_batch)

        level_image_batch = np.array(level_image_batch).transpose((0, 3, 1, 2))
        level_image_batch = torch.from_numpy(level_image_batch).float()



        if use_cuda:
            level_image_batch = level_image_batch.cuda()

        multi_level_image_batch.append(level_image_batch)
    return multi_level_image_batch

def compute_pyramid(image_batch,f,nL,ration,use_cuda=False):
    '''
    暂时发现使用这个构造图像金字塔精度高一点
    :param image_batch:
    :param f:
    :param nL:
    :param ration:
    :return:
    '''

    image_batch = image_batch.transpose(1,2).transpose(2,3)

    if use_cuda:
        image_batch = image_batch.cpu().numpy()
    else:
        image_batch = image_batch.numpy()
    multi_level_image_batch = []
    multi_level_image_batch.append(torch.from_numpy(image_batch.transpose((0,3,1,2))))
    current_ration = ration
    for level in range(1,nL):

        level_image_batch = []
        for image_item in image_batch:
            #tmp = cv2.filter2D(image_item,-1,f)
            #level_image = smi.imresize(tmp,size=current_ration)/255.0
            level_image = smi.imresize(image_item[:,:,0],size=current_ration)/255.0

            if len(level_image.shape) == 2:
                level_image = level_image[:,:,np.newaxis]
            level_image_batch.append(level_image)

        level_image_batch = np.array(level_image_batch).transpose((0,3,1,2))
        level_image_batch = torch.from_numpy(level_image_batch).float()

        if use_cuda:
            level_image_batch = level_image_batch.cuda()


        multi_level_image_batch.append(level_image_batch)
        current_ration = current_ration * ration

        # plt.figure()
        # plt.imshow(level_image_batch[0].squeeze())


    return multi_level_image_batch



def compute_pyramid_pytorch(image_batch,scaleTnf,filter,nL,ration,use_cuda=False):
    '''
    :param image_batch: [batch,channel,h,w]  Tensor
    :param f:
    :param nL:
    :param ration:
    :return:
    '''

    kernel = torch.Tensor(filter).unsqueeze(0).unsqueeze(0)

    if use_cuda:
        kernel = kernel.cuda()

    multi_level_image_batch = []
    multi_level_image_batch.append(image_batch)
    for level in range(1,nL):

        image_batch = scaleTnf(image_batch,ration)

        # 对图片进行高斯滤波
        # if level <= nL-3:
        #image_batch = F.conv2d(image_batch, kernel, padding=1)
        # plt.figure()
        # plt.imshow(image_batch[0].squeeze())

        multi_level_image_batch.append(image_batch)

    return multi_level_image_batch

class ScaleTnf:

    def __init__(self,use_cuda=False):
        self.theta_identity = torch.tensor([
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=torch.float).unsqueeze(0)      #[batch,2,3]

        if use_cuda:
            self.theta_identity = self.theta_identity.cuda()
    def __call__(self,image_batch, ration):
        batch_size, c, h, w = image_batch.size()
        out_size = torch.Size((batch_size, c, int(h * ration), int(w * ration)))
        grid = F.affine_grid(self.theta_identity.repeat(batch_size,1,1), out_size)
        output = F.grid_sample(image_batch, grid)
        return output




