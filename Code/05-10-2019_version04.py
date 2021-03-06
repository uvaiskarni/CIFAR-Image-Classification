import numpy as np
import matplotlib.pyplot as plt
from keras.datasets import cifar10
from keras import backend as K
from keras.utils.np_utils import to_categorical
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPool2D
from keras.optimizers import RMSprop
from keras.callbacks import ReduceLROnPlateau,EarlyStopping

#if K.backend()=='tensorflow':
   # K.set_image_dim_ordering("th")
  
 
def myGetModel(data):
    # CNN model
    model = Sequential()

    model.add(Conv2D(filters = 32, kernel_size = (3,3),padding = 'Same',
                     activation ='relu', input_shape = (32,32,3)))

    model.add(Conv2D(filters = 32, kernel_size = (3,3),padding = 'Same',
                     activation ='relu'))

    model.add(MaxPool2D(pool_size=(2,2)))

    model.add(Dropout(0.25))

    model.add(Conv2D(filters = 64, kernel_size = (2,2),padding = 'Same',
                     activation ='relu'))    
    
    model.add(Conv2D(filters = 64, kernel_size = (2,2),padding = 'Same',
                     activation ='relu'))

    model.add(MaxPool2D(pool_size=(2,2), strides = (2,2)))

    model.add(Dropout(0.25))

    model.add(Flatten())

    model.add(Dense(256, activation = "relu"))

    model.add(Dropout(0.5))

    model.add(Dense(10, activation = "softmax"))
    
    # Compile the model with optimizer
    model.compile(optimizer = RMSprop(lr=0.001,
                                      rho=0.9,
                                      epsilon=1e-8,
                                      decay=0.0) ,
                  loss = "categorical_crossentropy", metrics=["accuracy"])
    
    return(model)
  
def myFitModel(model,data):
  
    # setting the learniing rate using rLRO
    DynamiclearningRate = ReduceLROnPlateau(monitor='val_acc', 
                                            patience=2, 
                                            verbose=1, 
                                            #factor=0.5, 
                                            min_lr=0.00001)
    
    earlyStopping = EarlyStopping(monitor="val_loss",
                                 patience=5,
                                 verbose=1,
                                 restore_best_weights=True)
    
    # fitting model with train data and validating
    FitModel = model.fit(data.x_train,data.y_train,batch_size=100,epochs = 20,
                         validation_data = (data.x_valid, data.y_valid),
                         verbose = 2,callbacks=[DynamiclearningRate,earlyStopping])
    
    
    return(FitModel)

class CIFAR:
    def __init__(self,seed=0):
        # Get and split data
        data = self.__getData(seed)
        self.x_train_raw=data[0][0]
        self.y_train_raw=data[0][1]
        self.x_valid_raw=data[1][0]
        self.y_valid_raw=data[1][1]
        self.x_test_raw=data[2][0]
        self.y_test_raw=data[2][1]
        # Record input/output dimensions
        self.num_classes=10
        self.input_dim=self.x_train_raw.shape[1:]
         # Convert data
        self.y_train = to_categorical(self.y_train_raw, self.num_classes)
        self.y_valid = to_categorical(self.y_valid_raw, self.num_classes)
        self.y_test = to_categorical(self.y_test_raw, self.num_classes)
        self.x_train = self.x_train_raw.astype('float32')
        self.x_valid = self.x_valid_raw.astype('float32')
        self.x_test = self.x_test_raw.astype('float32')
        self.x_train  /= 255
        self.x_valid  /= 255
        self.x_test /= 255
        # Class names
        self.class_names=['airplane','automobile','bird','cat','deer',
               'dog','frog','horse','ship','truck']

    def __getData (self,seed=0):
        (x_train, y_train), (x_test, y_test) = cifar10.load_data()
        return self.__shuffleData(x_train,y_train,x_test,y_test,seed)
    
    def __shuffleData (self,x_train,y_train,x_test,y_test,seed=0):
        tr_perc=.75
        va_perc=.15
        x=np.concatenate((x_train,x_test))
        y=np.concatenate((y_train,y_test))
        np.random.seed(seed)
        np.random.shuffle(x)
        np.random.seed(seed)
        np.random.shuffle(y)
        indices = np.random.permutation(len(x))
        tr=round(len(x)*tr_perc)
        va=round(len(x)*va_perc)
        self.tr_indices=indices[0:tr]
        self.va_indices=indices[tr:(tr+va)]
        self.te_indices=indices[(tr+va):len(x)]
        x_tr=x[self.tr_indices,]
        x_va=x[self.va_indices,]
        x_te=x[self.te_indices,]
        y_tr=y[self.tr_indices,]
        y_va=y[self.va_indices,]
        y_te=y[self.te_indices,]
        return ((x_tr,y_tr),(x_va,y_va),(x_te,y_te))

    # Print figure with 10 random images, one from each class
    def showImages(self):
        fig = plt.figure(figsize=(8,3))
        for i in range(self.num_classes):
            ax = fig.add_subplot(2, 5, 1 + i, xticks=[], yticks=[])
            idx = np.where(self.y_valid_raw[:]==i)[0]
            features_idx = self.x_valid_raw[idx,::]
            img_num = np.random.randint(features_idx.shape[0])
            im = np.transpose(features_idx[img_num,::],(1,2,0))
            ax.set_title(self.class_names[i])
            plt.imshow(im)
        plt.show()   
        
def runImageClassification(seed):
    # Fetch data. You may need to be connected to the internet the first time this is done.
    # After the first time, it should be available in your system. On the off chance this
    # is not the case on your system and you find yourself repeatedly downloading the data, 
    # you should change this code so you can load the data once and pass it to this function. 
    print("Preparing data...")
    data=CIFAR(seed)
        
    # Create model 
    print("Creating model...")
    model=myGetModel(data)
    
    # Fit model
    print("Fitting model...")
    history=myFitModel(model,data)
    
    print("Evaluating model...")
    score=model.evaluate(data.x_test, data.y_test, verbose=0)
    print('Test accuracy:', score[1])
    
    # Plot the loss and accuracy curves for training and validation 
    fig, ax = plt.subplots(2,1)
    ax[0].plot(history.history['loss'], color='b', label="Training loss")
    ax[0].plot(history.history['val_loss'], color='r', label="validation loss",axes =ax[0])
    legend = ax[0].legend(loc='best', shadow=True)

    ax[1].plot(history.history['acc'], color='b', label="Training accuracy")
    ax[1].plot(history.history['val_acc'], color='r',label="Validation accuracy")
    legend = ax[1].legend(loc='best', shadow=True)
    

runImageClassification(seed = 7)