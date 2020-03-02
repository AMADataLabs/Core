####################################################
# SUPERVISED LEARNING: CLASSIFICATION AND PREDICTION
####################################################

####################
# DATA PREPROCESSING
####################

# Load Data
email_data <- read.table('C:/Users/jalee/Desktop/Email_Classification_Project/Train_Model/Processed_Data_for_Input/training_email_processed.csv', header=TRUE,sep=",")

# factorize booleans
email_data$teleph <- factor(email_data$teleph)
email_data$NumberedEmail <- factor(email_data$NumberedEmail)
email_data$MD <- factor(email_data$MD)
email_data$DR <- factor(email_data$DR)
email_data$DOC <- factor(email_data$DOC)

# take a look at the data for sanity check:
str(email_data)
head(email_data)

####################
# TRAIN AND TEST SET
####################
library(caret)
set.seed(1) # I did not set this prior to publishing the results
# create a train and test set
trainIndex <- createDataPartition(y = email_data$quality2, p = 0.7, list=F)
train <- email_data[trainIndex,]
test <- email_data[-trainIndex,]

########################
# MODELS AND PERFORMANCE
########################

# Notes on the libraries caret vs MLR
# Logistic Regression
# Penalized GLM
# Linear Discriminant Analysis
# Nonlinear Discriminant Analysis
# Partial Least Squares Discriminant
# Nearest Shrunked Centroid
# Flexible Discrimant Analysis
# Naive Bayes Classifier 
# K Nearest Neighbor
# SVM
# Neural Net
# Random Forest
# Tree Boosting
# Ensemble Method
# Performance Metric Comparison
# Summary and Examples of Misclassifications
# ROC, Lift, Gain, and Calibration Charts
# Multinomial Logit (if we seek multivariate)

#####################
# Caret Library
# the most popular machine learning library in R
# advantage: this library allows grid search over parameters
# define a resampling variable
ctrl <- trainControl(method='cv',
                     number=10,
                     summaryFunction = twoClassSummary,
                     classProbs = T)

ctrl2 <- trainControl(method='repeatedcv',
                    # 10-fold CV: number = 10
                    number = 10,
                    # repeat 10 times: compute average of 10 10-fold CV errors
                    # this parameter is only available for method='repeatedcv'
                    repeats=10,
                    # gives classification statistics
                    summaryFunction = twoClassSummary,
                    classProbs = T)

#######################
# MLR library
# the second most popular machine leanring library in R
# In MLR, we have to create a task an a learner. This means more code writing, but gives the user more flexibility and overview of what one is doing
makeLearner()


######################
# Logistic Regression
# glm
logisMod <- glm(quality2~., data=train, family=binomial)
logisModPred <- factor(ifelse(predict(logisMod, newdata=test)>0.5,1,0))
summary(logisMod)
confusionMatrix(data=logisModPred, reference=test$quality2)

# caret
logisMod <- train(quality2~., data=train,
                  method='glm',
                  metric='ROC',
                  trControl=ctrl)
logisModPred <- predict(logisMod, newdata=test)
summary(logisMod)
LRcm <- confusionMatrix(data=logisModPred, reference=test$quality2)
plot(varImp(logisMod,scale=F))

####################
# Penalized Logistic

# caret
# random search
penMod2 <- train(quality2~.,data=train,
                method='glmnet',
                tuneLength=20,
                preProc=c('center','scale'),
                metric='ROC', trControl=ctrl)
penModPred2 <- predict(penMod2, newdata=test)
confusionMatrix(data=penModPred2, reference=test$quality2)
plot(varImp(penMod,scale=F))

# grid search
# parameters to search for: 

penGrid <- expand.grid(.alpha=seq(0.1,0.9,by=0.05),
                       .lambda=seq(0.01,0.2,length=40))
penMod <- train(quality2~.,data=train,
                method='glmnet',
                tuneGrid=penGrid,
                preProc=c('center','scale'),
                metric='ROC', trControl=ctrl)
penModPred <- predict(penMod, newdata=test)
pencm <- confusionMatrix(data=penModPred, reference=test$quality2)
plot(varImp(penMod,scale=F))

##############################
# Linear Discriminant Analysis

# idea behind it: maximize the ratio of between group covariance/within group covariance quadratic sum
# the maximizing vector a (which is linear combination coefficient) is the eigenvector of eigendecomposition of W^-1*B
# eigenvectors are the sets of coefficients
# eigenvalue is weight to each eigenvector

# caret
ldaMod <- train(quality2~.,data=train,
                method='lda', 
                preProc=c('center','scale'),
                metric='ROC', 
                trControl=ctrl)
ldaModPred <- predict(ldaMod, newdata=test)
(ldacm <- confusionMatrix(data=ldaModPred, reference=test$quality2))
plot(varImp(ldaMod,scale=F))


#############################################
# Partial Least Squares Discriminant Analysis

# caret
# random search
plsdaMod2 <- train(quality2~.,data=train, 
                  method='pls',
                  tuneLength=20,
                  preProc=c('center','scale'),
                  metric='ROC',
                  trControl=ctrl)
plsdaModPred2 <- predict(plsdaMod2, newdata=test)
confusionMatrix(data=plsdaModPred2, reference=test$quality2)

# grid search
plsdaMod <- train(quality2~.,data=train, 
                  method='pls',
                  tuneGrid = expand.grid(.ncomp=1:10),
                  preProc=c('center','scale'),
                  metric='ROC',
                  trControl=ctrl)
plsdaModPred <- predict(plsdaMod, newdata=test)
plscm <- confusionMatrix(data=plsdaModPred, reference=test$quality2)
plot(varImp(plsdaMod,scale=F))

####################
# Nonlinear Discriminant Analysis

# mda
library(mda)
mdaMod <- mda(quality2~., data=train, subclasses=3)

# caret
# random search
mdaMod2 <- train(quality2~., data=train,
                method='mda',
                metric='ROC',
                tuneLength=20,
                trControl = ctrl)
mdaModPred2 <- predict(mdaMod2, newdata=test)
confusionMatrix(data=mdaModPred2, reference=test$quality2)

# grid search
mdaGrid <- expand.grid(.subclasses=1:8)
mdaMod <- train(quality2~., data=train,
                method='mda',
                metric='ROC',
                tuneGrid = mdaGrid,
                trControl = ctrl)
mdaModPred <- predict(mdaMod, newdata=test)
mdacm <- confusionMatrix(data=mdaModPred, reference=test$quality2)
plot(varImp(mdaMod,scale=F))

################################
# Flexible Discriminant Analysis

# mda and earth
library(mda)
library(earth)
fdaModel <- fda(quality2~., data = train, method = earth)
summary(fdaModel)
mdaModPred <- predict(mdaMod, newdata=test)
confusionMatrix(data=test$quality2, reference=mdaModPred)

# caret
# random search
fdaMod2 <- train(quality2~., data=train,
                method='fda',
                metric='ROC',
                tuneLength = 20,
                trControl = ctrl)
fdaModPred2 <- predict(fdaMod2, newdata=test)
confusionMatrix(data=fdaModPred2, reference=test$quality2)

# grid search
fdaGrid <- expand.grid(degree=1:5, nprune=1:10)
fdaMod <- train(quality2~., data=train,
                method='fda',
                metric='ROC',
                tuneGrid = fdaGrid,
                trControl = ctrl)
saveRDS(fdaMod, 'C:/Users/jalee/Desktop/Email_Classification_Project/Train_Model/fdaMod')
fdaModPred <- predict(fdaMod, newdata=test)
fdacm <- confusionMatrix(data=fdaModPred, reference=test$quality2)
plot(varImp(fdaMod,scale=F))

########################
# bagged FDA
bfdaGrid <- expand.grid(degree=1:5, nprune=1:10)
bfdaMod <- train(quality2~., data=train,
                method='fda',
                metric='ROC',
                tuneGrid = fdaGrid,
                trControl = ctrl)
fdaModPred <- predict(fdaMod, newdata=test)
fdacm <- confusionMatrix(data=fdaModPred, reference=test$quality2)
plot(varImp(fdaMod,scale=F))


########################
# Naive Bayes Classifier

# need to preprocess data

# e1071
library(e1071)
nbMod <- naiveBayes(train[,-2], train$quality2, type='raw')
nbModPred <- predict(nbMod, newdata=test)
(nbcm <- confusionMatrix(data=nbModPred, reference=test$quality2))

# klaR
library(MASS)
library(klaR)
nbMod <- NaiveBayes(train[,-2], train$quality2, type='class')
nbModPred <- predict(nbMod, newdata=test)
(nbcm <- confusionMatrix(data=nbModPred$class, reference=test$quality2))

# caret
# naive_bayes: laplace, usekernel, adjust
# nb: fL, usekernel, adjust
# nbDiscrete: smooth
# awnb (attribute weighting): smooth
# manb (model averaged): smooth, prior
# tan (tree augmented naive): score, smooth
# tanSearch (structure learner wrapper): 	k, epsilon, smooth, final_smooth, sp
# awtan (attribute weighting): score, smooth
nbMod <- train(quality2~top+email.name+email.domain+teleph+NumberedEmail+MD+DR+DOC, data=train,
               method='nbDiscrete', 
               trControl=ctrl,
               tuneGrid = data.frame(smooth=seq(0,10,1)))
nbModPred <- predict(nbMod, newdata=test)
(nbcm <- confusionMatrix(data=nbModPred, reference=test$quality2))
plot(varImp(nbMod,scale=F))

####################
# K-Nearest Neighbor

# fastNaiveBayes library: bernoulli naive bayes
mod <- fastNaiveBayes.bernoulli(email_data[,-quality2], email_data$quality2, laplace = 1) # laplace = smoothing parameter


# caret
knnGrid <- data.frame(.k=c(4*(0.5)+1,
                          20*(1:5)+1,
                          50*(2:9)+1))
knnMod <- train(quality2~.,data=train,
                method='knn',
                metric='ROC',
                preProc=c('center','scale'),
                tuneGrid = knnGrid,
                trControl=ctrl)
knnModPred <- predict(knnMod, newdata=test)
knncm <- confusionMatrix(data=test$quality2, reference=knnModPred)
plot(varImp(knnMod,scale=F))

############################
# Nearest Shrunken Centroid

# caret
nscGrid <- data.frame(.threshold=0:25)
nscMod <- train(quality2~.,data=train,
                method='pam',
                preProc=c('center','scale'),
                metric='ROC',
                trControl=ctrl)
nscModPred <- predict(nscMod, newdata=test)
nsccm <- confusionMatrix(data=nscModPred, reference=test$quality2)
plot(varImp(nscMod,scale=F))

########################
# Support Vector Machine

# e1071 library
library(e1071)
# radial kernel (choice of kernel matters)
# kernel choices: 'radial', 'linear', 'polynomial', and 'sigmoid'; use radial here in case data are non-linearly separable
# gamma = parameter to kernels (linear doesnt need this) and measures wiggliness of radial kernel; higher gamma leads to more overfitting
# cost = regularization term and imposes penalty on slack terms (all points violating the soft margin constraint and are between -1 and 1 will become support vectors)
# wiggly kernel requires high regularization to counteract overfitting; higher cost means fewer number of support vectors because it allows fewer points along the margin
# in other words, cost goes up, model reduces the number of violations by making margin narrower
# cross = number of folds for cross validation
# probability = allow for probabilistic output via using pseudolikelihood modeling
svm_mod <- svm(quality2~., data=train, method="C-classification", kernel="radial", gamma=0.1, cost=10, cross=10, probability=F) 

# caret
library(kernlab)
# random search
svmMod2 <- train(quality2~., data=train, 
                  method='svmRadial',
                  trControl=ctrl,
                  tuneLength=20,
                  metric='ROC') 
svmModPred2 <- predict(svmMod2, newdata=test)
confusionMatrix(data=svmModPred2, reference=test$quality2)
plot(varImp(svmMod2,scale=F))

# grid search
# sigma = parameter of radial kernel: higher sigma means wigglier separating hyperplane
# C = cost parameter: penalizes slack terms (misclassification)
# expand.grid() native function in R builds a dataframe of all combinations
svmGrid <- expand.grid(sigma=c(0.01,0.05,0.1,0.5,1,2,3,4,5,10), C=2^seq(from=-4,to=4,by=1))
svmMod <- train(quality2~., data=train, 
                method='svmRadial',
                metric='ROC',
                preProc = c('center','scale'),
                trControl=ctrl,
                tuneGrid=svmGrid)
svmModPred <- predict(svmMod, newdata=test)
svmcm <- confusionMatrix(data=svmModPred, reference=test$quality2)
plot(varImp(svmMod,scale=F))

#################
# Neural Net

# caret
# random search
nnMod2 <- train(quality2~., data=train, 
                 method='nnet',
                 trControl=ctrl,
                 tuneLength=20, 
                 metric='ROC',
                verbose=F)
nnModPred2 <- predict(nnMod2, newdata=test, type='class')
confusionMatrix(data=nnModPred2, reference=test$quality2)

# grid search
# takes 25 minutes
nnGrid <- expand.grid(.size=1:10, .decay=seq(0.1,2,by=0.1))
maxSize <- max(nnGrid$.size)
numWts <- maxSize*(ncol(train)+1) + maxSize + 1

nnMod <- train(quality2~., data=train, 
              method = 'nnet', 
              metric = 'ROC',
              preProc = c('center','scale','spatialSign'),
              tuneGrid = nnGrid, 
              trace = F,
              maxit = 2000, 
              maxWts = numWts,
              trControl = ctrl)
nnModPred <- predict(nnMod, newdata=test, type='class')
nncm <- confusionMatrix(data=test$quality2, reference=nnModPred)
plot(varImp(nnMod,scale=F))

######################################
# Random Forest

# randomForest
library(randomForest)
library(gplots)
library(RColorBrewer)
heatmap.2(t(importance(rfMod)[,1:4]),
          col=brewer.pal(9, 'Blues'),
          dend='none', trace='none', key=FALSE,
          margins=c(10,10),
          main='Variable importance by Quality'
)
# single tree dendogram
# https://cran.rstudio.com/web/packages/randomForestExplainer/vignettes/randomForestExplainer.html


# caret
# random search: takes 10~15 minutes
rfMod2 <- train(quality2~., data=train,
                method='rf',
                metric='ROC',
                tuneLength=10,
                trControl=ctrl,
                ntree=1500)
rfModPred2 <- predict(rfMod2, newdata=test)
confusionMatrix(reference=test$quality2, data=rfModPred2)
plot(varImp(rfMod2, scale=F, main="Variable Importance by Quality"))

# grid search # takes 10 minutes
modellist <- list()
rfGrid <- expand.grid(.mtry = c(sqrt(ncol(train))))
for (ntree in seq(500,3000,by=500)) {
  rfMod <- train(quality2~., data=train,
                 method='rf',
                 metric='ROC',
                 tuneGrid = rfGrid,
                 trControl=ctrl,
                 ntree=ntree)
  key <- toString(ntree)
  modellist[[key]] <- rfMod
}
rfMod <- modellist[6]
rfModPred <- predict(rfMod, newdata=test)
rfcm <- confusionMatrix(data=rfModPred$`3000`, reference=test$quality2)
plot(varImp(rfMod, scale=F, main="Variable Importance by Quality"))

###############
# Tree Boosting

# caret
# random search
tbMod2 <- train(quality2~.,data=train, 
               method='gbm', 
               trControl=ctrl, 
               tuneLength=10,
               metric='ROC',
               verbose=F)
tbModPred2 <- predict(tbMod2, newdata=test)
confusionMatrix(data=tbModPred2, reference=test$quality2)

# grid search
tbGrid <- expand.grid(n.trees=seq(50,1000,50), 
                      interaction.depth=c(30), 
                      shrinkage=c(0.1,0.05),
                      n.minobsinnode=1:10)
tbMod <- train(quality2~.,data=train, 
               method='gbm', 
               trControl=ctrl, 
               tuneGrid=tbGrid, 
               metric='ROC',
               verbose=F)
tbModPred <- predict(tbMod, newdata=test)
tbcm <- confusionMatrix(data=test$quality2, reference=tbModPred)
plot(varImp(tbMod,scale=F,main="Variable Importance by Quality"))

##########
# Ensemble
# majority vote method
# the reason this is good is because it will reduce variance of prediction (aka model variance)
ModelsPred <- data.frame(cbind(logisModPred,
                               penModPred,
                               ldaModPred,
                               mdaModPred,
                               plsdaModPred,
                               fdaModPred,
                               nscModPred,
                               nbcModPred,
                               knnModPred,
                               svmModPred,
                               nnModPred,
                               rfModPred,
                               tbModPred
                               ))
ensemblePred <- numeric(nrow(ModelsPred))
ensemblePred <- for (i in 1:length(ensemblePred)) {ensemblePred[i] <- ifelse(sum(ModelsPred[i]=='Good')>=7, 'Good', 'Bad')}
confusionMatrix(data=test$quality2, reference=tbModPred)

###############################
# Performance Metric Comparison

result.comparison <- data.frame(cbind(c(LRcm$overall[1:2],LRcm$byClass), # cbind accuracy, kappa, and other metrics together
                                      c(pencm$overall[1:2],pencm$byClass),
                                      c(ldacm$overall[1:2],ldacm$byClass),
                                      c(plscm$overall[1:2],plscm$byClass),
                                      c(mdacm$overall[1:2],mdacm$byClass),
                                      c(fdacm$overall[1:2],fdacm$byClass),
                                      c(knncm$overall[1:2],knncm$byClass),
                                      c(nsccm$overall[1:2],nsccm$byClass),
                                      c(svmcm$overall[1:2],svmcm$byClass),
                                      c(rfcm$overall[1:2],rfcm$byClass),
                                      c(tbcm$overall[1:2],tbcm$byClass)))
colnames(result.comparison)=c('Logistic Regression',
                             'Penalized Logistic Regression',
                             'Linear Discriminant Analysis',
                             'Partial Least Squares',
                             'Nonlinear Discriminant Analysis',
                             'Flexible Discriminant Analysis',
                             'K-Nearest Neighbor',
                             'Nearest Shrunken Centroid',
                             'Support Vector Machine',
                             'Random Forest',
                             'Gradient Boosting')
rownames(result.comparison)<-names(c(LRcm$overall[1:2],LRcm$byClass))
write.csv(result.comparison,"C:/Users/jalee/Desktop/Email_Classification_Project/result.comparison.csv")


#################################################
# Summary of Flexible Discriminant Analysis: documentation and interpretation 

# 1. overfitting on FDA

# 2. parameters:

# 3. train accuracy =  , test accuracy = 

# 4. coefficient values and their signs 

# 5. How to know the p-values? 


##########################
# Examples of good and bad


######################
# Receiver Operating Characteristic Curve using he library pROC
library(pROC)
fdaModPredProb <- predict(fdaMod, newdata=test, type='prob')
rocCurve <- roc(response=test$quality2,
                predictor=fdaModPredProb$Good,
                levels=levels(test$quality2))
auc(rocCurve)
plot(rocCurve, main='ROC Curve', legac.axes=T) # legacy.axes = F default; T means specificity is increasing


# ROC curve 2 using the library ROCR
library(ROCR)
RORCpred <- prediction(fdaModPredProb$Good, test$quality2)
# true positive rate vs false positive rate 
ROCRperf <- performance(RORCpred, 'tpr', 'fpr')
plot(ROCRperf, colorize=TRUE, text.adj=c(-0.2,1.7))

# sensitivity vs specificity
ROCRperf2 <- performance(RORCpred, 'sens', 'spec')
plot(ROCRperf2, colorize=TRUE, text.adj=c(-0.2,1.7))

# Sensitivity vs Specificity Plots
# sensitivity = TP, Specificity = TN
sens <- data.frame(x=unlist(performance(RORCpred, measure='sens', x.measure='cutoff')@x.values),
                   y=unlist(performance(RORCpred, measure='sens', x.measure='cutoff')@y.values))
spec <- data.frame(x=unlist(performance(RORCpred, measure='spec', x.measure='cutoff')@x.values),
                   y=unlist(performance(RORCpred, measure='spec', x.measure='cutoff')@y.values))
library(dplyr)
library(ggplot2)
sens %>% ggplot(aes(x,y)) +
  geom_line() +
  geom_line(data=spec, aes(x,y,col='red')) +
  scale_y_continuous(sec.axis=sec_axis(~., name='Specificity')) +
  labs(x='Cutoff', y='Specificity') +
  theme(axis.title.y.right = element_text(colour='red'), legend.position ='none')


# Lift Chart comparing two methodologies
library(caret)
liftCurve <- lift(test$quality2 ~ fdaModPredProb$Good)
liftCurve
## comparing two models
labs <- c(fdaModPredProb = 'FDA', rfModPredProb = 'RF')
liftCurve <- lift(test$quality2 ~ fdaModPredProb + rfModPredProb)
xyplot(liftCurve,
       auto.key = list(columns=2,
                       lines=T,
                       points=F))

# Calibration Plots
calCurve <- calibration(test$quality2 ~ fdaModPredProb + rfModPredProb)
calCurve
xyplot(calCurve, auto.key=list(columns=2))

# calculating each metric individually
posPredValue(data=fdaModPred, reference=test$quality2, positive='Good', prevalence=.9)  # adjust prevalence manually if you want to go hypothetical

sensitivity(data=fdaModPred, reference=test$quality2, positive='Good')
specificity(data=fdaModPred, reference=test$quality2, positive='Good')
posPredValue(data=fdaModPred, reference=test$quality2, positive='Good')
negPredValue(data=fdaModPred, reference=test$quality2, positive='Good')

#####################
# FEATURE SELECTION
#####################
# forward and backward elimination for regression modeling
LRmod <- step(LRmod, direction='both') # both = forward and backward selection
library(MASS)
LRmod <- stepAIC(LRmod, direction='both')

# recursive feature elimination
### general
svmFuncs <- caretFuncs
svmFuncs$summary <- fivestats
ctrl <- rfeControl(method='repeatedcv',
                   repeats=5,
                   verbose=T,
                   functions=svmFuncs,
                   index=index)
svmRFE <- rfe(y~., data,
             sizes='ROC',
             rfeControl=ctrl,
             method='svmRadial',
             tuneLength=12,
             preProc=c('center','scale'),
             trControl=trainControl(method='cv',
                                    verboseIter=F,
                                    classProbs=T))
svmRFE

# filter method
pScore <- function(x,y) {
  numX <- length(unique(x))
  if (numX > 2) {
    out <- t.test(x ~ y)$p.value
  } else {
    out <- fisher.test(factor(x), y)$p.value
  }
  out
}
scores <- apply(X=train[,-quality2],
                margin=2,
                FUN=pScore,
                y=train[,quality2])
scores

## p-value correction 
## Bonferroni
pCorrection <- function(score,x,y) {
  score <- p.adjust(score, 'bonferroni')
  keepers <- (score<=0.05)
  keepers
}

# caret has built-in functions for filter methods
# linear discriminant analysis -> ldaSBF
str(ldaSBF)
ldaWithPvalues <- ldaSBF
ldaWithPvalues$score <- pScore
ldaWithPvalues$summary <- fiveStats
ldaWithPvalues$filter <- pCorrection
sbfCtrl <- sbfControl(method='repeatedcv',
                      repeats=5,
                      verbose=T,
                      functions=ldaWithPvalues,
                      index=index)
ldaFilter <- sbf(pred, model$class,
                 tol=1.0e-12,
                 sbfControl=sbfCtrl)
ldaFilter

### random forest
library(varSelRF)
str(rfFuncs)
newRF <- rfFuncs
newRF$summary <- fiveStats
ctrl <- rfeControl(method='repeatedcv',
                   repeats=5,
                   verbose=T,
                   functions=newRF,
                   index=index)
rfRFE <- rfe(y~., data,
             sizes=varSeq,
             metric='ROC',
             rfeControl=ctrl)
rfRFE


###################################################################################################
# If we are using 4 category response, then we will use multilogit instead of logistic regression
# other methods can generlaize to multiple categories

#####################
# Multinomial Logit

# you first need to prepare the dataset such that quality has 4 categories not 2

# nnet 
library(nnet)
multilogMod <- multinom(quality~., data=train)
summary(multilogMod)
multilogModPred <- predict(multilogMod,newdata=test)
confusionMatrix(reference=test$quality,data=multilogModPred) 

# Interpretation Tool for multinomial
library(AER)
coeftest(multilogMod)

# caret
multilogGrid <- seq(0,2,by=0.1)
multilogMod <- train(quality~., data=train, 
                method='multinom',
                trControl=ctrl,
                metric='ROC',
                tuneGrid=mmultilogGrid)
multilogModPred <- predict(multilogMod,newdata=test)
confusionMatrix(reference=test$quality,data=multilogModPred) 


