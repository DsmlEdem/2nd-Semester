""" Main Script - Testing all Models at once"""

# Classic libraries
import numpy as np
import time
import rasterio
import os

# Sk learn
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Torch
from torch.utils.data import random_split
from torch.utils.data import DataLoader
import torch.nn as nn
import torch

# Data Augmentation
import albumentations as A

# Custom functions
from lib import segmentation_test_loop
from lib import TransferResNet
from lib import augmented_dataset
from lib import prepare_datasets
from lib import standard_dataset
from lib import MLP_Dataset
from lib import MLP_Net
from lib import training_loop
from lib import test_loop
from lib import CNN
from lib import UNet
from lib import CustomCmap
from lib import plot_confusion_matrix
from lib import predict_image
from lib import write_tif
from lib import plot_img_labels


# Main starts here
#%%
# The target names - 14 uses of land
target_names = np.array(['Dense Urban Fabric', 'Mineral Extraction Sites', 'Non Irrigated Arable Land',
                         'Fruit Trees', 'Olive Groves', 'Broad-leaved Forest', 'Coniferous Forest',
                         'Mixed Forest', 'Dense Sclerophyllous Vegetation', 'Sparce Scerophyllous Vegetation',
                         'Sparcely Vegetated Areas', 'Rocks and Sand', 'Water', 'Coastal Water'])
# Training & Validation Path
training_path = os.path.join(os.getcwd(),"HyRANK_satellite", "TrainingSet")
validation_path = os.path.join(os.getcwd(),"HyRANK_satellite", "ValidationSet")
prediction_path = os.path.join(os.getcwd(),"HyRANK_satellite", "Predictions")

random_state = 42 # Setting random state

# Visualize the satellite images in RGB
dioni_train = rasterio.open(os.path.join(training_path, "Dioni.tif"))
dioni_val = rasterio.open(os.path.join(training_path, "Dioni_GT.tif"))
loukia_train = rasterio.open(os.path.join(training_path, "Loukia.tif"))
loukia_val = rasterio.open(os.path.join(training_path, "Loukia_GT.tif"))

# Custom cmap
cmap = CustomCmap([204/255, 213/255, 228/255],[92/255, 120/255, 169/255])
#%%
plot_img_labels(dioni_train,dioni_val.read().squeeze(),
                list(target_names),"Dioni in RGB", "Dioni Labels", "DioniRGB",True)
plot_img_labels(loukia_train,loukia_val.read().squeeze(),
                list(target_names),"Loukia in RGB", "Loukia Labels","LoukiaRGB",True)
#%%
#################################################
####            Part 1 - Basic Models        ####
#################################################

# Preparing the datasets
""" 1.1 -  Train on both images - Bad approach
    because of information leakage on the test set"""
print(f"{5*'-'}> Part 1 - Testing some classic classifiers <{5*'-'}\n")
X_dioni, y_dioni = standard_dataset(dioni_train, dioni_val) # X_dioni shape: Labels x Channels
X_loukia, y_loukia = standard_dataset(loukia_train, loukia_val)
X = np.concatenate((X_dioni, X_loukia), axis = 0)
y = np.concatenate((y_dioni, y_loukia), axis=0)
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.33,
                                                    random_state=random_state)
print("- Training on both images at the same time ...\n")

######### Random Forest #########

clf_forest = RandomForestClassifier(max_depth=16, random_state=random_state)
tic = time.time()
print(f"- Training random forest ...")
clf_forest.fit(X_train, y_train)
print(f"- training completed in {time.time()-tic:.4f} sec(s)")
preds = clf_forest.predict(X_test)
print("- Results on the test set ...:\n")
print(classification_report(y_test, preds, target_names=target_names))
plot_confusion_matrix(y_true = y_test,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="Random Forest - Trained on both Images")
#%%
######### Custom MLP #########

# Check if cuda is available
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

in_features = dioni_train.count
out_features = len(target_names)
#%%
# Hyperparameters for training
batch_size = 64
epochs = 200
lr = 1e-5
loss_fn = nn.CrossEntropyLoss().to(device)

# Preparing datasets
train_set = MLP_Dataset(X,y)

p = int(0.8*len(train_set)) # 80 % for train, 20 % for test
train_set, test_set = random_split(train_set, [p, len(train_set)-p])
p = int(0.8*len(train_set))
train_set, val_set = random_split(train_set,[p, len(train_set)-p])
train_loader = DataLoader(train_set, batch_size=batch_size,
                          shuffle=True)
test_loader = DataLoader(test_set, batch_size=batch_size)
val_loader = DataLoader(val_set, batch_size=batch_size)

model = MLP_Net(in_features=in_features, out_features=out_features,
                layers=[256,512,256,128]).to(device)
tic = time.time()
print(f"- Training MLP ...")
model, train_loss, val_loss = training_loop(model,train_loader,val_loader,
                                            epochs,lr,loss_fn,regularization="L2",
                                            reg_lambda=1e-1,early_stopping=True,patience=30,
                                        verbose=False, title="MLP (trained on both images)")
mins, secs = divmod(time.time()-tic, 60)
print(f"\n- training completed in {mins} min(s) and {secs:.4f} sec(s)")

# %% Evaluation
print("- Results on the test set ...:\n")
preds, targets = test_loop(model, test_loader, device = device)
print(classification_report(targets, preds, target_names=target_names))
plot_confusion_matrix(y_true = targets,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="MLP - Trained on both Images",
                      ignore_index=True)

# %%
"""1.2 Training on Dioni validating on Loukia"""

print("- Training on Dioni validating on Loukia ...\n")
######### Random Forest #########
clf_forest = RandomForestClassifier(max_depth=16, random_state=random_state)
tic = time.time()
print(f"- Training random forest ...")
clf_forest.fit(X_dioni, y_dioni)
print(f"- training completed in {time.time()-tic:.4f} sec(s)")
preds = clf_forest.predict(X_loukia)
print("- Results on the test set ...:\n")
print(classification_report(y_loukia, preds, target_names=target_names))
plot_confusion_matrix(y_true = y_loukia,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="Random Forest - Trained only on Dioni")

#%%
######### Custom MLP #########
# Preparing datasets
train_set = MLP_Dataset(X_dioni,y_dioni)
test_set = MLP_Dataset(X_loukia,y_loukia)

p = int(0.8*len(train_set)) # 80 % for train, 20 % for test
train_set, val_set = random_split(train_set, [p, len(train_set)-p])
train_loader = DataLoader(train_set, batch_size=batch_size,
                          shuffle=True)
test_loader = DataLoader(test_set, batch_size=batch_size)
val_loader = DataLoader(val_set, batch_size=batch_size)

model = MLP_Net(in_features=in_features, out_features=out_features,
                layers=[256,512,256,128]).to(device)
tic = time.time()
print(f"- Training MLP ...")
model, train_loss, val_loss = training_loop(model,train_loader,val_loader,
                                            epochs,lr,loss_fn,regularization="L2",
                                            reg_lambda=1e-1,early_stopping=True,patience=30,
                                        verbose=False, title="MLP (trained on Dioni)")
mins, secs = divmod(time.time()-tic, 60)
print(f"\n- training completed in {mins} min(s) and {secs:.4f} sec(s)")

print("- Results on the test set ...:\n")
preds, targets = test_loop(model, test_loader, device = device)
print(classification_report(targets, preds, target_names=target_names))
plot_confusion_matrix(y_true = targets,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="MLP - Trained only on Dioni",
                      ignore_index=True)
# %%
"""Part 2 - CNN testing """
print(f"{5*'-'}> Part 2 - CNN's <{5*'-'}\n")
######### CNN with patches - no pretrained 85% overlapping #########

train_set, val_set, test_set = prepare_datasets(training_path=training_path,
                                                train_test_ratio=0.7, train_val_ratio=0.7,
                                                type="Patches",combined=True,patch_size=15,
                                                center_stride=1)
batch_size = 32
train_loader = DataLoader(train_set, batch_size = batch_size,
                          shuffle = True)
val_loader = DataLoader(val_set, batch_size = batch_size)
test_loader = DataLoader(test_set, batch_size = batch_size)
epochs = 200
lr = 1e-4
loss_fn = nn.CrossEntropyLoss().to(device)

model = CNN(channels_in = in_features, num_classes = out_features).to(device)
# %%
tic = time.time()
print(f"- Training CNN with patches - Maximum overlapping ...")
model, train_loss, val_loss = training_loop(model,train_loader,val_loader,
                                            epochs,lr,loss_fn,regularization="L2",
                                            reg_lambda=1e-3,early_stopping=True,patience=30,
                                        verbose=False, title="CNN - Trained on patches maximum overlapping")
mins, secs = divmod(time.time()-tic, 60)
print(f"\n- training completed in {mins} min(s) and {secs:.4f} sec(s)")

print("- Results on the test set ...:\n")
preds, targets = test_loop(model, test_loader, device = device)
print(classification_report(targets, preds, target_names=target_names))
plot_confusion_matrix(y_true = targets,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="CNN - Overlapping Patches",
                      ignore_index=True)
#%% Annotate Dioni
pred_img = predict_image(training_path,"Dioni",model,"center",
                         15,device)
plot_img_labels(dioni_train,pred_img,
                list(target_names),"Dioni in RGB", "Dioni Predictions with CNN",
                "PredDioniCNN")
write_tif(os.path.join(prediction_path,"DioniPredCNN.tif"),pred_img)
#%% Predictions with CNN
erato = rasterio.open(os.path.join(validation_path,"Erato.tif"))
kirki = rasterio.open(os.path.join(validation_path,"Kirki.tif"))
nefeli = rasterio.open(os.path.join(validation_path,"Nefeli.tif"))

erato_pred = predict_image(validation_path,"Erato",model,
                           "center",15,device)
kirki_pred = predict_image(validation_path,"Kirki",model,
                           "center",15,device)
nefeli_pred = predict_image(validation_path,"Nefeli",
                            model,"center",15,device)
# Erato
plot_img_labels(erato,erato_pred,
                list(target_names),"Erato in RGB", "Erato Predictions","EratoPredsCNN")
write_tif(os.path.join(prediction_path,"EratoPredCNN.tif"),erato_pred)
# Kirki
plot_img_labels(kirki,kirki_pred,
                list(target_names),"Kirki in RGB", "Kirki Predictions","KirkiPredsCNN")
write_tif(os.path.join(prediction_path,"KirkiPredCNN.tif"), kirki_pred)
# Nefeli
plot_img_labels(nefeli,nefeli_pred,
                list(target_names),"Nefeli in RGB", "Nefeli Predictions","NefeliPredsCNN")
write_tif(os.path.join(prediction_path,"NefeliPredCNN.tif"), nefeli_pred)


#%%

######### CNN with patches - no pretrained no overlapping #########

train_set, val_set, test_set = prepare_datasets(training_path=training_path,
                                                train_test_ratio=0.7, train_val_ratio=0.7,
                                                type="Patches",combined=True,patch_size=7,
                                                center_stride=6)
batch_size = 32
train_loader = DataLoader(train_set, batch_size = batch_size,
                          shuffle = True)
val_loader = DataLoader(val_set, batch_size = batch_size)
test_loader = DataLoader(test_set, batch_size = batch_size)
epochs = 300
lr = 1e-4
loss_fn = nn.CrossEntropyLoss().to(device)

model = CNN(channels_in = in_features, num_classes = out_features).to(device)
#%%
tic = time.time()
print(f"- Training CNN with patches - No overlapping...")
model, train_loss, val_loss = training_loop(model,train_loader,val_loader,
                                            epochs,lr,loss_fn,regularization="L2",
                                            reg_lambda=1e-4,early_stopping=True,patience=120,
                                        verbose=False, title="CNN trained on patches with no overlapping")
mins, secs = divmod(time.time()-tic, 60)
print(f"\n- training completed in {mins} min(s) and {secs:.4f} sec(s)")

print("- Results on the test set ...:\n")
preds, targets = test_loop(model, test_loader, device = device)
print(classification_report(targets, preds, target_names=target_names))
plot_confusion_matrix(y_true = targets,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="CNN - Non-Overlapping Patches",
                      ignore_index=True)

#%%
rgb = (23,11,7)
train_set, val_set, test_set = prepare_datasets(training_path=training_path,
                                                train_test_ratio=0.7, train_val_ratio=0.7,
                                                type="Patches",combined=True,patch_size=7,
                                                center_stride=6, channels=rgb)
batch_size = 32
#%%
transforms = A.Compose([
    A.VerticalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.OneOf([
        A.ElasticTransform(p=0.5, alpha=120, sigma=120 * 0.05, alpha_affine=120 * 0.03),
        A.GridDistortion(p=0.5),
        A.OpticalDistortion(distort_limit=1, shift_limit=0.5, p=0.5),
    ], p=0.8)])
#%%

train_set = augmented_dataset(train_set, transforms)
train_loader = DataLoader(train_set, batch_size = batch_size,
                          shuffle = True)
val_loader = DataLoader(val_set, batch_size = batch_size)
test_loader = DataLoader(test_set, batch_size = batch_size)

epochs = 300
lr = 1e-5
loss_fn = nn.CrossEntropyLoss().to(device)
model = TransferResNet(n_classes=out_features, freeze_head=False).to(device)

tic = time.time()
print(f"- Training ResNet on patches - No overlapping...")
model, train_loss, val_loss = training_loop(model,train_loader,val_loader,
                                            epochs,lr,loss_fn,regularization="L2",
                                            reg_lambda=1e-4,early_stopping=True,patience=50,
                                        verbose=False, title="ResNet on patches with no overlapping")
mins, secs = divmod(time.time()-tic, 60)
print(f"\n- training completed in {mins} min(s) and {secs:.4f} sec(s)")

print("- Results on the test set ...:\n")
preds, targets = test_loop(model, test_loader, device = device)
print(classification_report(targets, preds, target_names=target_names))
plot_confusion_matrix(y_true = targets,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="ResNet - Non Overlapping Patches",
                      ignore_index=True)

# %%

"""Part 3 - UNet Training"""
print(f"{5*'-'}> Part 3 - UNet <{5*'-'}\n")
train_set, val_set, test_set = prepare_datasets(training_path,0.75,0.7,
                                                "Cropped",crop_size = 32)
train_set = augmented_dataset(train_set,transforms,
                                  apply_on_target=True)
batch_size = 16

train_loader = DataLoader(train_set,batch_size=batch_size,
                           shuffle=True)
val_loader = DataLoader(val_set, batch_size=batch_size)
test_loader = DataLoader(test_set, batch_size= batch_size)

torch.cuda.empty_cache()

epochs = 500
lr = 1e-5
loss_fn = nn.CrossEntropyLoss(ignore_index=-1).to(device)

model = UNet(in_channels=176, out_channels=14,
             features = [128, 256, 512]).to(device)

tic = time.time()
print(f"- Training UNet on cropped dataset - 32x32 images...")
model, train_loss, val_loss = training_loop(model = model, train_loader=train_loader, val_loader=val_loader,
                                            lr=lr, epochs=epochs, loss_fn=loss_fn, regularization="L2",
                                            reg_lambda=1e-1, early_stopping=True, patience = 120,
                                            verbose=True, title = "UNet training")
mins, secs = divmod(time.time()-tic, 60)
print(f"\n- training completed in {mins} min(s) and {secs:.4f} sec(s)")
preds, targets = segmentation_test_loop(model = model,
                                            test_loader = test_loader,
                                            ignore_index=-1, device = device)
print(classification_report(targets, preds, target_names = target_names))
plot_confusion_matrix(y_true = targets,y_pred=preds,cmap=cmap,
                      target_names=target_names,title="UNet",
                      ignore_index=True)

#%% Part 4 - Predictions with UNet

erato_pred = predict_image(validation_path,"Erato",model,
                           "corner",32,device)
kirki_pred = predict_image(validation_path,"Kirki",model,
                           "corner",32,device)
nefeli_pred = predict_image(validation_path,"Nefeli",
                            model,"corner",32,device)
# Erato
plot_img_labels(erato,erato_pred,
                list(target_names),"Erato in RGB", "Erato Predictions","EratoPredsUNet")
write_tif(os.path.join(prediction_path,"EratoPredUNet.tif"),erato_pred)
# Kirki
plot_img_labels(kirki,kirki_pred,
                list(target_names),"Kirki in RGB", "Kirki Predictions", "KirkiPredsUNet")
write_tif(os.path.join(prediction_path,"KirkiPredUNet.tif"), kirki_pred)
# Nefeli
plot_img_labels(nefeli,nefeli_pred,
                list(target_names),"Nefeli in RGB", "Nefeli Predictions", "NefeliPredsUNet")
write_tif(os.path.join(prediction_path,"NefeliPredUNet.tif"), nefeli_pred)