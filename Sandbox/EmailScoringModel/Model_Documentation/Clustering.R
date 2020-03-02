############
# CLUSTERING
############

####################
# TRAIN & TEST SPLIT
####################

set.seed(1)
trainIndex <- createDataPartition(y = email_data$quality2, p = 0.7, list=F)
train <- email_data[trainIndex,]
test <- email_data[-trainIndex,]

# train and test split on predictors only
predictor <- email_data[,-2]
trainp <- predictor[trainIndex,]
testp <- predictor[-trainIndex,]


###############
# VISUALIZATION
###############
# Visualization for Quick Look at Data
# clustering plot
library(cluster)
clusplot(trainp, train$quality2, color=TRUE, shade=TRUE, labels=4, lines=0, main="Quality Clusters")

##########
# MODELING
##########

# 1. K-Mode
# 2. Latent class Analysis
# 3. Association Basket

############
# I. K-modes (K-means analogue for categorical data)

# write the function
kmodes=function (data = data, nclust = nclust, niterations = niterations, nloops = nloops, seed = seed) 
{
  prevMAF = -1
  niterations = 25
  set.seed(seed)
  for (i in 1:nloops) {
    z = fun.kmodes(data = data, nclust = nclust,niterations=niterations)
    if (z$MAF > prevMAF) {
      prevMAF = z$MAF
      ind = i
      z.old = z
    }
  }
  return(list(data = z.old$Data, 
              Group = z.old$Groups, Centroids = z.old$Centroids,  
              Cluster.Sizes= z.old$Cluster.Sizes,
              MAF = z.old$MAF, iteration = ind, 
              seed = seed))
}

fun.kmodes=function (data = data, nclust = nclust,niterations=niterations) 
{
  data=as.data.frame(data)
  nam=names(data)
  data=apply(data,2,factor)
  M = nrow(data)
  N = ncol(data)
  K = nclust
  S = sample(1:K,M,replace=TRUE)
  W = matrix("NA", K, N)
  datahat=matrix("NA",M,N)
  i = 1
  while ((i <= niterations)) {
    for(j in 1:N) {
      W[,j]=tapply(data[,j],S,fun.mod)
    }
    
    hst= 0
    #               print(W)
    for(j in 1:M) {
      tmp=rep(0,K)
      for (k in 1:K){
        
        ttt = (data[j,])==(W[k,])
        tmp[k]= length(ttt[ttt==TRUE])		
        
      }	
      l = seq(1:K)[tmp==max(tmp)]
      if(length(l) == 1) S[j]=l 
      if(length(l) > 1) S[j] = sample(l,1)
      datahat[j,] = W[S[j],]
      hst=hst+max(tmp)
    }	
    #                print(c(i, hst))
    
    #			for(j in 1:M) {
    #				for(n in 1:N) {
    #				if(!is.na(data[j,n]) && (datahat[j,n] == data[j,n])) hst[i] = hst[i]+1
    
    i=i+1
  }
  W=data.frame(W)
  names(W) = nam
  W = W[sort(unique(S)),]
  if(nrow(W) >1) {row.names(W) = sort(unique(S))}    
  rrr = list(Groups = S, Cluster.Sizes = table(S), Centroids = W, MAF = hst/(M*N))
  
  
  return(rrr)
}

fun.mod=function(x){
  
  y=factor(x)
  z=table(y)
  zz=z[z==max(z)]
  n=names(zz)
  if(length(n) > 1) n=sample(n,1)
  return(n)
  
  
}

# application
# train
x2 <- kmodes(data=trainp, nclust=2, nloops=30, seed=1)
x3 <- kmodes(data=trainp, nclust=3, nloops=30, seed=1)
x4 <- kmodes(data=trainp, nclust=4, nloops=30, seed=1)
x5 <- kmodes(data=trainp, nclust=5, nloops=30, seed=1)
x6 <- kmodes(data=trainp, nclust=6, nloops=30, seed=1)
x7 <- kmodes(data=trainp, nclust=7, nloops=30, seed=1)
x8 <- kmodes(data=trainp, nclust=8, nloops=30, seed=1)
x9 <- kmodes(data=trainp, nclust=9, nloops=30, seed=1)
x10 <- kmodes(data=trainp, nclust=10, nloops=30, seed=1)
x11 <- kmodes(data=trainp, nclust=11, nloops=30, seed=1)
x12 <- kmodes(data=trainp, nclust=12, nloops=30, seed=1)
x13 <- kmodes(data=trainp, nclust=13, nloops=30, seed=1)
x14 <- kmodes(data=trainp, nclust=14, nloops=30, seed=1)
x15 <- kmodes(data=trainp, nclust=15, nloops=30, seed=1)
MAF_train <- c(x2$MAF, x3$MAF, x4$MAF, x5$MAF, x6$MAF, x7$MAF, x8$MAF, x9$MAF, x10$MAF, x11$MAF, x12$MAF, x13$MAF, x14$MAF, x15$MAF)
plot(2:15,MAF_train,main="Matches Accounted For Scree Plot: train", xlab="Number of Clusters", ylab="MAF",col=4,type="l")
# test
y2 <- kmodes(data=testp, nclust=2, nloops=30, seed=1)
y3 <- kmodes(data=testp, nclust=3, nloops=30, seed=1)
y4 <- kmodes(data=testp, nclust=4, nloops=30, seed=1)
y5 <- kmodes(data=testp, nclust=5, nloops=30, seed=1)
y6 <- kmodes(data=testp, nclust=6, nloops=30, seed=1)
y7 <- kmodes(data=testp, nclust=7, nloops=30, seed=1)
y8 <- kmodes(data=testp, nclust=8, nloops=30, seed=1)
y9 <- kmodes(data=testp, nclust=9, nloops=30, seed=1)
y10 <- kmodes(data=testp, nclust=10, nloops=30, seed=1)
y11 <- kmodes(data=testp, nclust=11, nloops=30, seed=1)
y12 <- kmodes(data=testp, nclust=12, nloops=30, seed=1)
y13 <- kmodes(data=testp, nclust=13, nloops=30, seed=1)
y14 <- kmodes(data=testp, nclust=14, nloops=30, seed=1)
y15 <- kmodes(data=testp, nclust=15, nloops=30, seed=1)
MAF_test <- c(y2$MAF, y3$MAF, y4$MAF, y5$MAF, y6$MAF, y7$MAF, y8$MAF, y9$MAF, y10$MAF, y11$MAF, y12$MAF, y13$MAF, y14$MAF, y15$MAF)
plot(2:15,MAF_test,main="Matches Accounted For Scree Plot: test", xlab="Number of Clusters", ylab="MAF",col=4,type="l")

x4$Centroids
x4$Cluster.Sizes

x8$Centroids
x8$Cluster.Sizes

y4$Centroids
y4$Cluster.Sizes

y8$Centroids
y8$Cluster.Sizes

##########################
# 2. Latent Class Analysis (instead of hard classification, gives probabilistic output)
##########################
library(poLCA)

# convert data into factors
f1 = with(trainp,
          cbind(top, teleph, email.domain, email.name, NumberedEmail, MD, DR, DOC) ~ 1)
result.2 <- poLCA(f1,trainp,nclass=2,nrep=10,tol=.001,verbose=FALSE)
result.3 <- poLCA(f1,trainp,nclass=3,nrep=10,tol=.001,verbose=FALSE)
result.4 <- poLCA(f1,trainp,nclass=4,nrep=10,tol=.001,verbose=FALSE)
result.5 <- poLCA(f1,trainp,nclass=5,nrep=10,tol=.001,verbose=FALSE)
result.6 <- poLCA(f1,trainp,nclass=6,nrep=10,tol=.001,verbose=FALSE)
result.7 <- poLCA(f1,trainp,nclass=7,nrep=10,tol=.001,verbose=FALSE)
result.8 <- poLCA(f1,trainp,nclass=8,nrep=10,tol=.001,verbose=FALSE)

result..2 <- poLCA(f1,testp,nclass=2,nrep=10,tol=.001,verbose=FALSE)
result..3 <- poLCA(f1,testp,nclass=3,nrep=10,tol=.001,verbose=FALSE)
result..4 <- poLCA(f1,testp,nclass=4,nrep=10,tol=.001,verbose=FALSE)
result..5 <- poLCA(f1,testp,nclass=5,nrep=10,tol=.001,verbose=FALSE)
result..6 <- poLCA(f1,testp,nclass=6,nrep=10,tol=.001,verbose=FALSE)
result..7 <- poLCA(f1,testp,nclass=7,nrep=10,tol=.001,verbose=FALSE)
result..8 <- poLCA(f1,testp,nclass=8,nrep=10,tol=.001,verbose=FALSE)
# compare by BIC
bicresult <- c(result.2$bic, result.3$bic, result.4$bic, result.5$bic, result.6$bic, result.7$bic, result.8$bic)
plot(2:8,bicresult,main="BIC: trainp",xlab="number of classes",ylab="BIC",type="l")

bicresultest <- c(result..2$bic, result..3$bic, result..4$bic, result..5$bic, result..6$bic, result..7$bic, result..8$bic)
plot(2:8,bicresultest,main="BIC:test",xlab="number of classes",ylab="BIC",type="l")
# bic is the lowest for 4 classes

# summary
# likelihood 
result.4$probs
# prior
summary(factor(result.4$predclass)) # distribution of classes
result.4$P # proportion of classes

#######################
# 3. Association Rules
#######################
# only on sparse dataset
library(arules)
library(arulesViz)

trainp_ar <- lapply(trainp[,c('top', 'spec', 'teleph', 'email_domain', 'email_name', 'NumberedEmail', 'MD')], factor)
trainp.trans_ar <- as(trainp_ar, "transactions")
summary(trainp.trans_ar)

test_ar <- lapply(testp[,c('top', 'spec', 'teleph', 'email_domain', 'email_name', 'NumberedEmail', 'MD')], factor)
test.trans_ar <- as(test_ar, "transactions")
summary(trainp.trans_ar)

newrules_trainp <-- apriori(trainp.trans_ar, parameter=list(supp=0.01,conf=0.1,target="rules", maxlen=5))
# why is taking too long?
summary(newrules_trainp)
inspect(subset(newrules,lift>3))
plot(newrules)
plot(newrules, interactive=TRUE)
head(sort(newrules,by='lift'),50)
plot(newrules, method="graph", control=list(type="items"))

