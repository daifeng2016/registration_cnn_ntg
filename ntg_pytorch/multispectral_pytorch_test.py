
import cv2
import torch
from torch.utils.data import DataLoader
from skimage import io
import matplotlib.pyplot as plt
import numpy as np
import torch.nn.functional as F

from datasets.provider.randomTnsData import RandomTnsPair
from datasets.provider.singlechannelData import SingleChannelPairTnf
from datasets.provider.test_dataset import TestDataset
from ntg_pytorch.register_func import estimate_aff_param_iterator, affine_transform
from tnf_transform.img_process import NormalizeImageDict
from visualization.train_visual import VisdomHelper

if __name__ == '__main__':

    use_cuda = torch.cuda.is_available()

    env = "ntg_pytorch"
    vis = VisdomHelper(env)
    # test_image_path = '/home/zlk/datasets/coco_test2017_n2000'
    # label_path = 'datasets/row_data/label_file/coco_test2017_n2000_custom_20r_param.csv'
    #
    # dataset = TestDataset(test_image_path,label_path,transform=NormalizeImageDict(["image"]))
    # dataloader = DataLoader(dataset,batch_size=1,shuffle=False,num_workers=4,pin_memory=True)
    # pair_generator = RandomTnsPair(use_cuda=use_cuda,output_size=(480, 640))

    # for batch_idx,batch in enumerate(dataloader):
    #     if batch_idx % 5 == 0:
    #         print('test batch: [{}/{} ({:.0f}%)]'.format(
    #             batch_idx, len(dataloader),
    #             100. * batch_idx / len(dataloader)))
    #
    #     pair_batch = pair_generator(batch)
    #     source_image_batch = pair_batch['source_image']
    #     target_image_batch = pair_batch['target_image']
    #     theta_GT_batch = pair_batch['theta_GT']
    #
    #     p = estimate_aff_param_iterator(source_image_batch,target_image_batch,use_cuda=use_cuda)
    #
    #     print(p)

    # img1 = io.imread('datasets/row_data/multispectral/Ir.jpg')
    # img3 = io.imread('datasets/row_data/multispectral/Itrot2.jpg')
    # img2 = io.imread('datasets/row_data/multispectral/Itrot3.jpg')

    img1 = io.imread('datasets/row_data/multispectral/000000001439_t.jpg')
    img2 = io.imread('datasets/row_data/multispectral/000000001439_s.jpg')
    img3 = io.imread('datasets/row_data/multispectral/000000001439_s.jpg')

    # img1 = img1[:, :, 0][ np.newaxis,:, :]
    # img2 = img2[:, :, 0][ np.newaxis,:, :]

    img1 = img1[:, :, 2][np.newaxis,:,:]
    img2 = img2[:, :, 0][np.newaxis,:,:]
    img3 = img3[:, :, 0][np.newaxis,:,:]

    # img1 = (img1.astype(np.float32) / 255 - 0.485) / 0.229
    # img2 = (img2.astype(np.float32) / 255 - 0.456) / 0.224
    # img3 = (img3.astype(np.float32) / 255 - 0.456) / 0.224

    img1 = img1.astype(np.float32) / 255
    img2 = img2.astype(np.float32) / 255
    img3 = img3.astype(np.float32) / 255


    source_batch = np.stack((img2,img3),0)
    target_batch = np.stack((img1,img1),0)

    source_batch = torch.from_numpy(source_batch)
    target_batch = torch.from_numpy(target_batch)

    # source_batch = source_batch.index_select(0,torch.tensor([0]))
    # target_batch = target_batch.index_select(0,torch.tensor([0]))



    p = estimate_aff_param_iterator(source_batch, target_batch, use_cuda=use_cuda)

    print(p)

    img1 = img1[0,:, :]
    img2 = img2[0,:, :]
    img3 = img3[0,:, :]


    im2warped = affine_transform(img2,p[0].cpu().numpy())
    im3warped = affine_transform(img3,p[1].cpu().numpy())

    # vis.showImage(torch.from_numpy(im2warped),win='im2',title='im2wrap')
    # vis.showImage(torch.from_numpy(im3warped),win='im3',title='im3wrap')

    plt.imshow(img1, cmap='gray')  # 目标图片
    plt.figure()
    plt.imshow(img2, cmap='gray')  # 待变换图片
    plt.figure()
    plt.imshow(img3, cmap='gray')  # 待变换图片
    plt.figure()
    plt.imshow(im2warped, cmap='gray')
    plt.figure()
    plt.imshow(im3warped, cmap='gray')
    plt.show()