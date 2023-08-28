dane <- read.csv("danewieksze.csv", sep=";", dec=",")
dane[10,] <- c(0, 0, 0, 0, 1, 1, 1)
dane <- dane[-7,]

S.P <- function(pu=1, pd=1){
  df <- data.frame(rowSums(dane[2:4]^pu/dane[5:7]^pd))
  colnames(df) <- "S"
  return(df)
}

S <- S.P(1, 1)

df <- data.frame(x=S$S, y=dane$Uzyskane)

fit.log <- lm(y~log(x + 1), data = df)

xaxis <- seq(0, 40, by = 1)
yaxis <- fit.log$coefficients[1] + fit.log$coefficients[2] * log(xaxis + 1)

std <- sd(fit.log$residuals)

plot(df, pch=19)
lines(xaxis, yaxis)
lines(xaxis, yaxis + std, lty = "dashed")
lines(xaxis, yaxis - std, lty = "dashed")
