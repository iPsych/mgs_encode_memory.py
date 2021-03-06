library(dplyr)
path<-sprintf("%s%s", getwd(), "/mgs_encode_memory.py/analysis")
source(sprintf("%s%s",path,"/eyetracking.R"))
files <- list.files(path=sprintf("%s%s",path,"/runs"), pattern="*.txt", full.names=TRUE, recursive=FALSE)

GetSpread <- function(fname) {
  
  # source(eyetracking.R)
  data <- read_avotec(fname) %>%
    select(c(ld8, runno, trial, event, x_gaze, side, totaltime))
  
  ## SCORE ##
  
  # Average of last 90 data points for each id->side->event->trial
  data.mt90 <- data %>%
    group_by(trial, event, side, ld8, runno) %>%
    summarise(mt90=mean(tail(x_gaze,90))) %>%
    ungroup() %>%
    mutate(side=ifelse(event=="iti",lag(side),side)) %>%
    spread(event, mt90)
  
  # Near/Right = 1; Near/Left = -1
  data.mt90$side_num <- grepl("Right",data.mt90$side) %>%
    ifelse(1,-1)
  
  # Trial order:
  #  iti -> [cue -> img] -> [isi -> mgs]
  # Scoring:
  #  0 (best) --> 2 (worst)
  #  0 = side_num == ic == mi
  #  1 = side_num == ic != mi
  #  2 = side_num != ic (=/!= mi)
  
  data.sides <- data.mt90 %>%
    mutate(ic=(img-cue)/abs(img-cue), mi=(mgs-isi)/abs(mgs-isi), score=ifelse(side_num==ic,ifelse(ic==mi,0,1),2))
  
  ## DATA QUALITY ##
  
  trial_scores <- data.sides %>%
    select(c(trial, score, ld8, runno)) %>%
    merge(data, by=c("trial","ld8", "runno"))
  
  return(trial_scores)
  #return(data.sides)
}

# Apply scoring to files[1:last_file] times
doAll <- function() {
  last_file <- 30
  #scored.out <- lapply(files[1:last_file], function(fname) tryCatch(GetSpread(fname), error=function(x) NULL)) %>% bind_rows()
  scored.out <- lapply(files[1:last_file], function(fname) tryCatch(GetSpread(fname), error=function(x) NULL)) %>% bind_rows()
}

# Retrieve large row-bound dataframe
scored.out <- suppressWarnings(doAll())

# data for mgs + img
mgs_data <- scored.out %>% 
  #select(c(ld8, runno, trial, score, event, totaltime)) %>%
  filter(event %in% c("mgs","img"))

 trial_start_times <- mgs_data %>%
  group_by(ld8, runno, trial, event) %>%
  summarise(mtime=min(totaltime))

 run_start_times <- mgs_data %>%
   group_by(ld8, runno) %>%
   summarise(mtime=min(totaltime))

ctimes <- merge(mgs_data, trial_start_times)

ctimes$adjusted_time <- ctimes$totaltime-(ctimes$mtime)

ctimes<-ctimes %>% select(-mtime)

ss<- ctimes %>%
  arrange(ld8, runno, trial, event) %>%
  filter(!is.na(side)) #%>%

### PLOTS ###

ss %>%
  filter(score==0, event=='mgs') %>%
  ggplot()+aes(x=adjusted_time, y=x_gaze)+geom_smooth(aes(color=ld8, group=paste(ld8)), se=FALSE)+xlim(0,1.0)+facet_wrap(~side)

## TODO: filter out wild outlying junk data from frame

fitted_models <- ss %>%
  filter(score==0, event=='mgs') %>%
  group_by(ld8, runno, trial, side) %>%
  do(model=lm(x_gaze ~ adjusted_time, data=.))

# use lapply to just grab slope



#ss %>%
#  filter(score==0, event=='mgs') %>%
#  lm(data=.,x_gaze~adjusted_time)

#ss %>%
#  ggplot()+aes(x=adjusted_time, y=x_gaze)+geom_smooth(aes(color=side, group=paste(trial,runno)), se=FALSE)+ylim(-2,2)+xlim(0,1.0)+facet_wrap(ld8 ~ event~side)


# Box plot
#  x = ld8
#  y = score
#  Jitter points shown (colored by run)
#gg_box <- scored.out %>%
#  ggplot()+aes(x=ld8,y=score)+geom_boxplot()+geom_jitter(aes(color=as.factor(run)))