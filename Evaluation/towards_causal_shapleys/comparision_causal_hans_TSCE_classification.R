# Laden Sie zusätzliche benötigte Pakete
library(arrow)
library(feather)
library(keras)
library(tensorflow)
library(dplyr)
library(magrittr)
library(shapr)
library(tidyr)
library(xgboost)
library(caret)
source("R/sina_plot.R")



subDirName <- "TSCE"
data_path <- "../data/shapley_tsce_classification.csv"

dir.create(subDirName)
patient_data <- read.csv(data_path, header = TRUE)


# Aufteilung in Trainings-, Validierungs- und Testdaten
train_ratio <- 0.85
validation_ratio <- 0.1
train_index <- sample(1:nrow(patient_data), round(nrow(patient_data) * train_ratio))
train_data <- patient_data[train_index, ]
remaining_data <- patient_data[-train_index, ]

validation_index <- sample(1:nrow(remaining_data), round(nrow(remaining_data) * (validation_ratio/(1-train_ratio))))
validation_data <- remaining_data[validation_index, ]
test_data <- remaining_data[-validation_index, ]


x_train_prep <- train_data %>% select(Lagged_Age, Lagged_Nutrition, Lagged_Health, Lagged_Mobility, Age, Nutrition, Health)
y_train_prep <- train_data$Mobility

x_validation_prep <- validation_data %>% select(Lagged_Age, Lagged_Nutrition, Lagged_Health, Lagged_Mobility, Age, Nutrition, Health)
y_validation_prep <- validation_data$Mobility

x_test_prep <- test_data %>%select(Lagged_Age, Lagged_Nutrition, Lagged_Health, Lagged_Mobility, Age, Nutrition, Health)
y_test_prep <- test_data$Mobility


# Training data
x_train <- as.matrix(x_train_prep)
y_train_nc <- as.matrix(y_train_prep) # not centered
y_train <- y_train_nc - mean(y_train_nc) 

# Validation data
x_validation <- as.matrix(x_validation_prep)
y_validation_nc <- as.matrix(y_validation_prep) # not centered
y_validation <- y_validation_nc - mean(y_train_nc)

# Test data
x_test <- as.matrix(x_test_prep)
y_test_nc <- as.matrix(y_test_prep) # not centered
y_test <- y_test_nc - mean(y_train_nc) 



# Some Hypertuning
# Create DMatrix for training and validation data
dtrain <- xgb.DMatrix(data = x_train, label = y_train_nc)
dvalidation <- xgb.DMatrix(data = x_validation, label = y_validation_nc)

# Define watchlist
watchlist <- list(train = dtrain, validation = dvalidation)

# Set the parameters for binary classification
params <- list(
  objective = "binary:logistic",
  eval_metric = "logloss",
  eta = 0.3,
  max_depth = 10
  # alpha = 1,
  # lambda = 1,
  # subsample = 0.8,
  # colsample_bytree = 0.8
)

# Perform cross-validation
cv_results <- xgb.cv(
  params = params,
  data = dtrain,
  nrounds = 5000,
  nfold = 5, # Number of folds for cross-validation
  early_stopping_rounds = 50,
  verbose = 1
)

# Get the best number of rounds
best_nrounds <- cv_results$best_iteration

# Train the final model
model <- xgb.train(
  params = params,
  data = dtrain,
  nrounds = best_nrounds,
  verbose = 1
)


#x_test <- x_test[1:500, ]


# Make predictions
preds <- predict(model, x_test)
# Convert predictions to class labels
labels <- as.integer(preds > 0.5)

partial_order <- list(c(1,2,3,4), c(5, 6), c(7))
confounding <- TRUE

indices_0 <- which(labels == 0)
indices_1 <- which(labels == 1)
x_test_0 <- x_test[indices_0, ]
x_test_1 <- x_test[indices_1, ]
num_rows <- 500 
x_test_0_sample <- head(x_test_0, n = num_rows)
x_test_1_sample <- head(x_test_1, n = num_rows)




x_test <- x_test_1_sample
pred_for <- "_for_above_average"

explainer_symmetric <- shapr(x_train, model)                    
p <- mean(y_train_nc)

explanation_causal <- explain(
  x_test,
  approach = "causal",
  explainer = explainer_symmetric,
  prediction_zero = p,
  ordering = partial_order,
  confounding = confounding,
  seed = 2020
)
sina_causal <- sina_plot(explanation_causal)
ggsave(paste(subDirName, "/symmetric_sina_plot_causal", pred_for, ".pdf", sep=""), sina_causal, height = 12, width = 12)
shapley_values <- explanation_causal$dt
feature_values <- explanation_causal$x_test
combined_df <- cbind(shapley_values, feature_values)
colnames(combined_df) <- c(paste0(colnames(shapley_values), "_Shapley"), 
                           paste0(colnames(feature_values), "_Value"))
write.csv(combined_df, file = paste(subDirName,  "/combined_df", pred_for, ".csv", sep=""))





x_test <- x_test_0_sample
pred_for <- "_for_below_average"

explainer_symmetric <- shapr(x_train, model)                    
p <- mean(y_train_nc)

explanation_causal <- explain(
  x_test,
  approach = "causal",
  explainer = explainer_symmetric,
  prediction_zero = p,
  ordering = partial_order,
  confounding = confounding,
  seed = 2020
)
sina_causal <- sina_plot(explanation_causal)
ggsave(paste(subDirName, "/symmetric_sina_plot_causal", pred_for, ".pdf", sep=""), sina_causal, height = 12, width = 12)



shapley_values <- explanation_causal$dt
feature_values <- explanation_causal$x_test
combined_df <- cbind(shapley_values, feature_values)
colnames(combined_df) <- c(paste0(colnames(shapley_values), "_Shapley"), 
                           paste0(colnames(feature_values), "_Value"))
write.csv(combined_df, file = paste(subDirName,  "/combined_df", pred_for, ".csv", sep=""))


#source("R/parallel.R")
#create_parallel_plot(explanation_causal, paste(subDirName, "/parallel_coordinates_plot_causal", pred_for, ".pdf", sep=""))


#x_test <- x_test_1_sample
#pred_for <- "_for_above_average"
#explainer_asymmetric <- shapr(x_train, model, asymmetric = TRUE, ordering = partial_order)
#p <- mean(y_train)
#explanation_asymmetric <- explain(
#  x_test,
#  approach = "causal",
#  explainer = explainer_asymmetric,
#  prediction_zero = p,
#  ordering = partial_order,
#  confounding= confounding,
#  asymmetric = TRUE,
#  seed = 2020
#)

#sina_causal <- sina_plot(explanation_asymmetric)
#ggsave(paste(subDirName, "/asymmetric_sina_plot_causal", pred_for, ".pdf", sep=""), sina_causal, height = 12, width = 12)




#x_test <- x_test_0_sample
#pred_for <- "_for_below_average"
#explainer_asymmetric <- shapr(x_train, model, asymmetric = TRUE, ordering = partial_order)
#p <- mean(y_train)
#explanation_asymmetric <- explain(
#  x_test,
#  approach = "causal",
#  explainer = explainer_asymmetric,
#  prediction_zero = p,
#  ordering = partial_order,
#  confounding= confounding,
#  asymmetric = TRUE,
#  seed = 2020
#)

#sina_causal <- sina_plot(explanation_asymmetric)
#ggsave(paste(subDirName, "/asymmetric_sina_plot_causal", pred_for, ".pdf", sep=""), sina_causal, height = 12, width = 12)











