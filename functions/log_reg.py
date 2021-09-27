import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics



def logistic_regression(series, cnf=1, acc=1, prec=1, rec=1):
    # Logistics Regression
    series['return_m'] = np.where(series['return_m']>=0, 1, 0)
    X_train, X_test, y_train, y_test = train_test_split(series['imi'], series['return_m'], test_size=0.25, random_state=0)
    logreg = LogisticRegression()
    logreg.fit(np.array(X_train).reshape(-1, 1),y_train)
    y_pred = logreg.predict(np.array(X_test).reshape(-1, 1))
    if cnf==1:
        cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
    else:
        cnf_matrix = 0
    if acc==1:
        accuracy = metrics.accuracy_score(y_test, y_pred)
    else:
        accuracy = 0
    if prec==1:
        precision = metrics.precision_score(y_test, y_pred)
    else:
        precision = 0
    if rec==1:
        recall = metrics.recall_score(y_test, y_pred)
    else:
        recall = 0
    print('cnf_matrix')
    print(cnf_matrix)
    print("Accuracy:", accuracy)
    print("Precision:", precision)
    print("Recall:", recall)

    return cnf_matrix, accuracy, precision, recall