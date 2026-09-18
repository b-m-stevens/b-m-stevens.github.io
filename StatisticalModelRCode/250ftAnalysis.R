library(tidyverse)
library(emmeans)
library(splines)
library(readxl)
library(lme4)
library(dplyr)

#Read Data (250 ft. Bus Stops)
crash <- read.csv("Crashes250ftBusStopNICC.csv", na = c("#N/A", "NA"))

bus_ref <- read.csv("Bus Stops Data - Reference.csv")  # adjust path/sheet if needed

bus_int <- read.csv("BusStops1400ftIntersectionNI.csv")   # adjust path

# 2. Attach stopabbr to each crash via NEAR_FID ----
crash2 <- crash %>%
  left_join(
    bus_ref %>% 
      mutate(stopabbr = as.character(stopabbr)),
    by = c("NEAR_FID" = "FID")
  )

bus_int_single <- bus_int %>%
  group_by(uta_stopid) %>%
  slice_min(order_by = NEAR_DIST, n = 1, with_ties = FALSE) %>%
  ungroup()

crash3 <- crash2 %>%
  left_join(
    bus_int_single %>%
      mutate(uta_stopid = as.character(uta_stopid)),
    by = c("stopabbr" = "uta_stopid"),
    suffix = c("", "_stop_int")
  ) %>%
  rename(
    CrashStopDist = NEAR_DIST,          # if this is the crash→stop distance
    StopIntDist   = NEAR_DIST_stop_int  # stop→intersection distance
  )

crash3 <- crash3 %>%
  mutate(
    StopAtIntersection = if_else(StopIntDist <= 50, 1L, 0L),
    # Create Pedestrian by checking if either column is Y
    Pedestrian = if_else(Pedestri_1 == "Y" | Bicycle__1 == "Y", 1L, 0L)
  ) %>%
  rename(
    Bus_Stop_Location = Bus.Stop.Location,
    Bus_Stop_Land_Use = Bus.Stop.Land.Use
  )

crash3 <- crash3 %>%
  mutate(Bus_Stop_Land_Use = fct_collapse(as.character(Bus_Stop_Land_Use),
                                          "Residential/Mixed" = c("Single Home", "Apartment", "Mixed Use"),
                                          "Commercial"        = c("Commercial", "Business"),
                                          "Agricultural"      = c("Undeveloped", "Farming", "Industrial"),
                                          "Institutional"     = c("Government", "School", "Church", "Hospital", "Library", "Transit station"),
                                          "Recreational"      = c("Recreational"),
                                          "Empty"             = c(" ")
  ))
#Re-level Land Use to Commercial 
crash3$Bus_Stop_Land_Use <- relevel(factor(crash3$Bus_Stop_Land_Use), ref = "Commercial")

# Re-level Location to Nearside
crash3$Bus_Stop_Location <- relevel(factor(crash3$Bus_Stop_Location), ref = "NS")

crash3$DOT_AADT <- as.numeric(as.character(crash3$DOT_AADT))

crash3$AvgBoard <- as.numeric(as.character(crash3$AvgBoard))

crash3$SPEED_LMT <- as.numeric(as.character(crash3$SPEED_LMT))

crash3$CrashStopDist <- round(crash3$CrashStopDist, 1)

crash3$StopIntDist <- round(crash3$StopIntDist, 1)

#Resolves empty strings
# This replaces "" and " " with NA for every column in the dataframe
crash3[crash3 == "" | crash3 == " "| crash3 == "Empty"] <- NA

# Then, drop the empty factor levels from all variables at once
crash3 <- droplevels(crash3)
#Modeling
crash3$Pedestrian <- factor(crash3$Pedestrian)
model4 <- glm(Pedestrian ~ ns(CrashStopDist, 2) + 
                ns(SPEED_LMT, 2) + 
                DOT_AADT + 
                AvgBoard +
                AvgAlighting +
                Intersecti + 
                Bus_Stop_Location + 
                Bus_Stop_Land_Use +
                StopIntDist +
                ns(CrashStopDist, 2)*Bus_Stop_Location,
              data = crash3, family = binomial)
summary(model4)
drop1(model4, test='Chisq')
#summary(crash3)
newdat<-data.frame(SPEED_LMT = 40, DOT_AADT = 25000, AvgBoard = 5, 
                   AvgAlighting = 6, Intersecti = "Y", 
                   Bus_Stop_Location = "FS", Bus_Stop_Land_Use = "Commercial",
                   StopIntDist = 154.303, CrashStopDist = seq(0.58, 340.27,length.out = 100))
#Use the median values of each predictor category to hold them all constant

newdat$pred1 <- predict(model4,newdat,type = "response")
plot(pred1~CrashStopDist,data = newdat, type = "l", xlab = "Distance of a Crash from Bus Stop", ylab = "Probability (%) a Crash is VRU Related",main = "VRU Crash Probability 250 ft.")
#Use the median values of each predictor category to hold them all constant

newdata<-data.frame(CrashStopDist = 140.4, DOT_AADT = 25000, AvgBoard = 5, 
                   AvgAlighting = 6, Intersecti = "Y", 
                   Bus_Stop_Location = "FS", Bus_Stop_Land_Use = "Commercial",
                   StopIntDist = 154.303, SPEED_LMT = seq(0, 65,length.out = 100))
#Use the median values of each predictor category to hold them all constant

newdata$pred1 <- predict(model4,newdata,type = "response")
plot(pred1~SPEED_LMT,data = newdata, type = "l", xlab = "Speed Limit (mph)", ylab = "Probability (%) a Crash is VRU Related",main = "VRU Crash Probability 250 ft.")
#Use the median values of each predictor category to hold them all constant

tmp.w <- as.numeric(names(model4$y))
model4.1 <- update(model4, . ~ ns(CrashStopDist, 2) + 
                     ns(SPEED_LMT, 2) + 
                     DOT_AADT + 
                     AvgBoard +
                     Intersecti + 
                     Bus_Stop_Location + 
                     Bus_Stop_Land_Use +
                     StopIntDist +
                     ns(CrashStopDist, 2)*Bus_Stop_Location, subset=tmp.w)
anova(model4.1, model4)
summary(model4.1)
drop1(model4.1, test='Chisq')
library(emmeans)
em4.1 <- emmeans(model4.1, ~Bus_Stop_Land_Use)
plot(em4.1, type="response", xlab = "Probability (%) a Crash is VRU Related (250 ft.)", ylab = "Bus Stop Land Use", main = "VRU Crash Probability 250 ft.")
plot(pairs(em4.1, type="response"))
em4.2 <- emmeans(model4.1, ~Bus_Stop_Location)
plot(em4.2, type="response", xlab = "Probability (%) a Crash is VRU Related (250 ft.)", ylab = "Bus Stop Location", main = "VRU Crash Probability 250 ft.")
# Get the estimated marginal means (predicted probabilities) for each location
location_means <- emmeans(model4.1, ~ Bus_Stop_Location, type = "response")
# See the predicted probability for each specific location
print(location_means)

# Perform pairwise comparisons to see which specific locations differ from one another, fdr adjustment
pairs(location_means, adjust = "none")
exp(coef(model4.1))
exp(confint(model4.1))
