############################
# Exploratory Data Analysis
############################

# Load Data
email_data <- read.table('C:/Users/jalee/Desktop/Email_Classification_Project/Train_Model/Processed_Data_for_Input/training_email_processed.csv', header=TRUE,sep=",")

#####################
# VARIABLE IMPORTANCE
####################

##################
# Filter Approach
library(caret)
# ROC curve analysis is performed on each predictor
# output is the AUC
filterVarImp(email_data[,-2],email_data$quality2)
# visualization

####################
# Relief Statistics
library(CORElearn)
# estimator: Relief and ReliefF algorithms (ReliefF, cost-sensitive ReliefF, ...), gain ratio, gini-index, MDL, DKM, information gain
attrEval(quality2~.,email_data,estimator='Relief') # 1991 Kira and Rendel measure
attrEval(quality2~.,email_data,estimator='InfGain') # information gain
attrEval(quality2~.,email_data,estimator='Gini') # Gini index
attrEval(quality2~.,email_data,estimator='DKM') # Dietterich, Kearns, Mansour measure
attrEval(quality2~.,email_data,estimator='GainRatio') # normalized information gain preventing bias to multi-valued attributes
attrEval(quality2~.,email_data,estimator='MDL') # minimum description length with bias to multi-valued attributes
# permutation of relief scores
library(AppliedPredictiveModeling)
pRelief <- permuteRelief(email_data[,-2],email_data$quality2,estimator="ReliefFequalK") # permutation aproach to determining the relative magnitude of relief scores
pRelief$observed # observed scores
pRelief$standardized # standardized predictor scores

##################################
# Maximal Information Coefficients
library(minerva)
?mine


########################
# MEASURE OF ASSOCIATION  
########################
#############
# Cramer's V
# Since all variables are categorical, we cannot compute correlation as we do for numeric variables. But! we can do something similar called Cramer's V and others.
library(grid)
library(vcd)
# VCD library contains association statistics such as the pearson chi-squared test (chisq.test = significance test), 
# likelihood ratio chi-squared test, contingency coefficient
# and Cramer's V (unlike test that shows significance, this shows size of association)
# need contingency table as input
ctable <- xtabs(~quality + email_domain, data=email_data)
assocstats(ctable) #0.451 for Cramer's V between email_domain and quality
ctable2 <- xtabs(~quality + email_name, data=email_data)
assocstats(ctable2) #0.225 for Cramer's V between email_name and quality
ctable3 <- xtabs(~quality + top, data=email_data)
assocstats(ctable3) # 0.501 between top and quality
# this is the wrapper function for all the codes above
catcorr <- function(vars, dat) sapply(vars, function(y) sapply(vars, function(x) assocstats(table(dat[,x], dat[,y]))$cramer))
(res <- catcorr(vars=c('email_domain', 'email_name','top','quality'), dat=email_data))

#####################
# Mutual Information
# Mutual information (MI) quantifies the amount of information needed to express one variable with the help of another variable. 
# defined as KL divergence between joint and product of marginals
# If two variables are independent of each other, their MI is zero, else it will be greater than zero.
# we want to know how much knowing one variable tells about the other
# This is a more general approach to correlation
# determine how similar the joint distribution is to the product of marginal by ratio of joint to product of marginals
# defined as KL divergence between joint and product of marginals
# re-expressed as difference between entropy minus conditional entropy
# reduction in uncertainty about X after observing Y
# can measure non-linear relationship
library(infotheo)
catmi <- mutinformation(email_data)

####################
# Association Tests
# odds ratio and statistical test of association
library(stats)
# fisher test (computationally prohitive for large data)
fisher.test(table(x,y))
# chi-square
chisq.test(table(x,y))

#################
# VISUALIZATION
#################

##################
# Data Description
library(DataExplorer)
plot_str(email_data, type="d")

library(ggplot2)
library(dplyr)

#########################
# Univariate Relationship
# Distributions
# Waffle Chart
var <- email_data$quality
nrows <- 10
df <- expand.grid(y=1:nrows, x=1:nrows)
cat_table <- round(table(var)*((nrows*nrows)/(length(var))))
df$quality <- factor(rep(names(cat_table), cat_table))
p <- ggplot(df, aes(x=x,y=y,fill=quality)) +
    geom_tile(color='black', size=0.5) +
    scale_x_continuous(expand=c(0,0)) + 
    scale_y_continuous(expand=c(0,0), trans='reverse') +
    scale_fill_brewer(palette='Set3')+
    labs(title='Waffle Chart', subtitle='Quality of Emails')
p + theme(plot.title = element_text(size = rel(1.2)),
          axis.text = element_blank(),
          axis.title = element_blank(),
          axis.ticks = element_blank(),
          legend.title = element_blank(),
          legend.position = "right")

# barplots
top_positions = c("resident","dpc", "retired", "unclassified", "admin","semiretired", "train", "research", "npc", "tempout", "inactive")
ggplot(email_data, aes(x=top)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  scale_x_discrete(limits=top_positions) +
  xlab('type of Practice') + ylab("Number of Observations") +
  ggtitle('Type of Practice Distribution')

quality_positions = c('Good','Failed(2001)','Unsubscribed','complained')
ggplot(email_data, aes(x=quality)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  scale_x_discrete(limits=quality_positions) +
  xlab('Quality') + ylab("Number of Observations") +
  ggtitle('Quality Distribution')

ggplot(email_data, aes(x=teleph)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  xlab('Telephone') + ylab("Number of Observations") +
  ggtitle('Has Telephone? Distribution')

email_positions = c('gmail','edu','etc','hotmail','msn','yahoo','comcast','aol','health','outlook','cox.net','rr')
ggplot(email_data, aes(x=email_domain)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  scale_x_discrete(limits=email_positions) +
  xlab('Email_Domain') + ylab("Number of Observations") +
  ggtitle('Email Domain Distribution')

name_positions = c('If_Fl', 'Ff_Fl','no_name','Dif_Person','Only_L','If_Il','Ff_Il','Only_F')
ggplot(email_data, aes(x=email_name)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +    
  scale_x_discrete(limits=name_positions) +
  xlab('Email Name') + ylab("Number of Observations") +
  ggtitle('Email Name Distribution')
  
ggplot(email_data, aes(x=NumberedEmail)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  xlab('Numbered Email') + ylab("Number of Observations") +
  ggtitle('Numbered Email Distribution')

ggplot(email_data, aes(x=MD)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  xlab('MD') + ylab("Number of Observations") +
  ggtitle('MD Distribution')

ggplot(email_data, aes(x=DR)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  xlab('DR') + ylab("Number of Observations") +
  ggtitle('DR Distribution')

ggplot(email_data, aes(x=DOC)) +
  geom_bar(fill = 'purple', width=0.5) + 
  coord_flip() +
  xlab('DOC') + ylab("Number of Observations") +
  ggtitle('DOC Distribution')

##########
# Two Way
# Bivariate Relationships

# 1. correlation plot
library(corrplot)
corrplot(res, type = "upper", order = "hclust", 
         tl.col = "black", tl.srt = 45)

# 1.5 Mutual Information Plot
library(ggplot2)
library(reshape2) # used for 'melt' function
# reorder the mutual information matrix according to the correlation coefficient
reorder_data <- function(x){
  # Use correlation between variables as distance
  dd <- as.dist((1-x)/2)
  hc <- hclust(dd)
  x <-x[hc$order, hc$order]
}
catmi <- melt(reorder_data(round(mutinformation(email_data),2))) # melt is a format requisite to doing heatmap in ggplot2 
ggheatmap <- ggplot(data = catmi, aes(Var2, Var1, fill = value))+
  geom_tile(color = "white")+
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-2,2), space = "Lab", 
                       name="Mutual\nInformation") +
  theme_minimal()+ 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, 
                                   size = 12, hjust = 1))+
  coord_fixed() # ensures that one unit on the x-axis is the same length as one unit on the y-axis
ggheatmap + 
  geom_text(aes(Var2, Var1, label = value), color = "black", size = 4) +
  theme(
    axis.title.x = element_blank(),
    axis.title.y = element_blank(),
    panel.grid.major = element_blank(),
    panel.border = element_blank(),
    panel.background = element_blank(),
    axis.ticks = element_blank(),
  ) +
  labs(title='Mutual Information Heatmap')

# 2. jitterplots
ggplot(email_data, aes(quality,teleph)) +
  geom_jitter(aes(teleph=quality), size = 0.5) +
  ggtitle('Quality and Teleph')

ggplot(email_data, aes(quality,MD)) +
  geom_jitter(aes(MD=quality), size = 0.5) +
  ggtitle('Quality and MD')

ggplot(email_data, aes(quality,DR)) +
  geom_jitter(aes(MD=quality), size = 0.5) +
  ggtitle('Quality and DR')

ggplot(email_data, aes(quality,DOC)) +
  geom_jitter(aes(MD=quality), size = 0.5) +
  ggtitle('Quality and DOC')

ggplot(email_data, aes(quality,NumberedEmail)) +
  geom_jitter(aes(NumberedEmail=quality), size = 0.1) +
  ggtitle('Quality and Numbered Email')

ggplot(email_data, aes(quality, email_domain)) +
  geom_jitter(aes(email_domain=quality), size = 0.1) +
  ggtitle('Quality and Email Domain')

ggplot(email_data, aes(quality, email_name)) +
  geom_jitter(aes(email_name=quality), size = 0.1) +
  ggtitle('Quality and Email Name')

ggplot(email_data, aes(quality,top)) +
  geom_jitter(aes(teleph=quality), size = 0.5) +
  ggtitle('Quality and Type of Practice')


# 3. Stacked Bar plot
# Now make two way contingency tables for the following graphs
# quality vs domain
quality_email_domain_df <- data.frame(table(email_data$quality, email_data$email_domain)) #ggballoonplot only takes in dataframe as input

g <- ggplot(email_data, aes(email_domain))
g + geom_bar(aes(fill=quality), width=0.5) + 
  theme(axis.text.x = element_text(angle=60, vjust=0.6)) +
  labs(title='Stacked Barplot',
       subtitle='Email Domain across Quality')

g <- ggplot(email_data, aes(top))
g + geom_bar(aes(fill=quality), width=0.5) + 
  theme(axis.text.x = element_text(angle=60, vjust=0.6)) +
  labs(title='Stacked Barplot',
       subtitle='Type of Practice across Quality')

g <- ggplot(email_data, aes(teleph))
g + geom_bar(aes(fill=quality), width=0.5) + 
  theme(axis.text.x = element_text(angle=60, vjust=0.6)) +
  labs(title='Stacked Barplot',
       subtitle='Telephone across Quality')

g <- ggplot(email_data, aes(email_name))
g + geom_bar(aes(fill=quality), width=0.5) + 
  theme(axis.text.x = element_text(angle=60, vjust=0.6)) +
  labs(title='Stacked Barplot',
       subtitle='Email Name across Quality')


# 4. Balloon Plot
library(ggpubr)
quality_email_domain <- table(email_data$quality, email_data$email_domain)
quality_email_domain_df <- data.frame(table(email_data$quality, email_data$email_domain)) #ggballoonplot only takes in dataframe as input
ggballoonplot(quality_email_domain_df, fill='value')+
  scale_fill_viridis_c(option='C')

quality_top <- table(email_data$quality, email_data$top)
quality_top_df <- data.frame(quality_top) #ggballoonplot only takes in dataframe as input
ggballoonplot(quality_top_df, fill='value')+
  scale_fill_viridis_c(option='E')

quality_email_name <- table(email_data$quality, email_data$email_name)
quality_email_name_df <- data.frame(quality_email_name) #ggballoonplot only takes in dataframe as input
ggballoonplot(quality_email_name_df, fill='value')+
  scale_fill_viridis_c(option='A')


# 5. Correspondence analysis: using factor analysis to group data points together (reduce 6-7 dimensions into two - dimensionality reduction method)
# quality vs email_domain
library(FactoMineR)
library(factoextra)
quality_email_domain <- table(email_data$quality, email_data$email_domain)
quality_domain_ca <- CA(quality_email_domain, graph=FALSE)
fviz_ca_biplot(quality_domain_ca, repel=TRUE)

quality_email_name <- table(email_data$quality, email_data$email_name)
quality_email_ca <- CA(quality_email_name, graph=FALSE)
fviz_ca_biplot(quality_email_ca, repel=TRUE)

#############
# Three Way
# Trivariate Relationships: 3 way contingency tables and their visualization

# email_domain vs email_name by qualities
threewaytab <- xtabs(~email_domain + email_name+quality, data=email_data)
library(dplyr)
email_data_subset <- email_data[,c(1,5,6)]
agg <- count(email_data, email_domain, email_name, quality)
agg <- count_(email_data_subset, names(email_data_subset))
head(agg)
xtabs(n~ email_domain + email_name +quality, data=agg)

# 1. Stacked Bar Graph
p <- ggplot(agg, aes(x=email_domain, y=n)) + 
  geom_bar(
    aes(fill=email_name), stat='identity', color='white',
    position=position_dodge(0.9)) +
  facet_wrap(~quality) +
  fill_palette('jco')
p + theme(axis.text.x = element_text(angle=60))

# 2. Balloon Plot
ggballoonplot(agg, x='email_domain', y='email_name', size='n',
              fill='n', facet.by='quality',
              ggthene= theme_bw()) +
  scale_fill_viridis_c(option='C')

# email_domain vs top by qualities
threewaytab <- xtabs(~email_domain + top + quality, data=email_data)
library(dplyr)
email_data_subset <- email_data[,c(1,2,5)]
agg <- count(email_data, email_domain, top, quality)
agg <- count_(email_data_subset, names(email_data_subset))
head(agg)
xtabs(n~ email_domain + top +quality, data=agg)

ggballoonplot(agg, x='email_domain', y='top', size='n',
              fill='n', facet.by='quality',
              ggthene= theme_bw()) +
  scale_fill_viridis_c(option='C')
  
# 3. Mosaic Plot
library(vcd)
mosaic(threewaytab, shade=TRUE, legend=TRUE) # too crowded
