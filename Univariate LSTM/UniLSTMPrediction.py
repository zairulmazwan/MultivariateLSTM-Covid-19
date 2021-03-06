import numpy
import matplotlib.pyplot as plt
import pandas as pd
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot

# fix random seed for reproducibility
numpy.random.seed(7)

# load the dataset
col = ["total_admission_UK"]
#dataframe = pd.read_csv('../Datasets/UKCovid-Rawdata.csv', usecols=col, engine='python')
dataframe = pd.read_csv('../Datasets/UKCovid-Rawdata_1.csv', usecols=col, engine='python')
dataframe.dropna(inplace=True)

dataset = dataframe.values
dataset = dataset.astype('float32')

#print(dataset[-5:,:])


# normalize the dataset
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset)


# split into train and test sets
train_size = int(len(dataset) * 0.75)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
print(len(train), len(test))



# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return numpy.array(dataX), numpy.array(dataY)



def runExperiment (data, iter):
	# reshape into X=t and Y=t+1
	look_back = 1
	trainX, trainY = create_dataset(train, look_back)
	testX, testY = create_dataset(test, look_back)


	# reshape input to be [samples, time steps, features]
	trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
	testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))


	# create and fit the LSTM network
	model = Sequential()
	model.add(LSTM(50, input_shape=(1, look_back)))
	model.add(Dense(1))
	model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
	#model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)


	#model.compile(loss='mae', optimizer='adam')

	# fit network
	history = model.fit(trainX, trainY, epochs=100, batch_size=15, validation_data=(testX, testY), verbose=2, shuffle=False)
	# plot history
	pyplot.plot(history.history['loss'], label='train')
	pyplot.plot(history.history['val_loss'], label='test')
	pyplot.legend()
	#pyplot.show()


	# make predictions
	trainPredict = model.predict(trainX)
	testPredict = model.predict(testX)
	# invert predictions
	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY])
	testPredict = scaler.inverse_transform(testPredict)
	testY = scaler.inverse_transform([testY])
	# calculate root mean squared error
	trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
	print('Train Score: %.2f RMSE' % (trainScore))
	testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
	print('Test Score: %.2f RMSE' % (testScore))
	data.append(testScore)

	# shift train predictions for plotting
	trainPredictPlot = numpy.empty_like(dataset)
	print("dataset shape : ", dataset.shape)
	trainPredictPlot[:, :] = numpy.nan
	trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
	# shift test predictions for plotting
	testPredictPlot = numpy.empty_like(dataset)
	testPredictPlot[:, :] = numpy.nan
	testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict
	# plot baseline and predictions
	plt.plot(scaler.inverse_transform(dataset))
	plt.plot(trainPredictPlot)
	plt.plot(testPredictPlot)
	plt.title("Admission Prediction (Univariate) - Iter "+str(iter), y=1.0, loc='center')
	#plt.show()
	plt.savefig("../Results/Univariate/res_univ"+str(iter)+".png")
	plt.clf()

iter = 26
data = []

for i in range(1,iter):
	runExperiment(data, i)

print(data)
result=pd.DataFrame(data)
result.to_csv("../Results/Univariate/ExperimentUniv_Results.cvs")
