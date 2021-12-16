#suppress warnings and command line output
zz <- file("sinkmessages.rout", open = "wt")
sink(zz, type = "message")
options(warn=-1)

suppressMessages(suppressWarnings(library(readxl)))
suppressMessages(suppressWarnings(library(ggplot2)))
suppressMessages(suppressWarnings(library(lubridate)))
suppressMessages(suppressWarnings(library(dplyr)))
suppressMessages(suppressWarnings(library(tidyr)))
suppressMessages(suppressWarnings(library(gmodels)))
suppressMessages(suppressWarnings(library(forcats)))

#prevents RPLOTS from being generated
#remove if debugging in rstudio
pdf(NULL)


#initialisation 
graphics_date <- Sys.Date()
args <- commandArgs(trailingOnly=TRUE)
data_file_name <- args[1] 
country <- args[2]
keyword <- args[3]
dir <- args[4]


df <- read_excel(data_file_name)

#read your own df here for testing
#dir <- ''
#df <- read_excel('haiti time series.xlsx')

#Date
df$endDate <- ymd(df$endDate)
current_date <- max(df$endDate)

df$reac_total <- rowSums(df[9:17])

df_graphic <- df[df$searched_keyword == keyword,]
df_graphic_hist <- df_graphic[df_graphic$endDate!=current_date,]
df_graphic_curr <- df_graphic[df_graphic$endDate==current_date,]


hist_mn <- mean(df_graphic_hist$hitCount)
reg <- lm(df_graphic_hist$hitCount~1)
mean_ll <- confint(reg)[1]
mean_ul <- confint(reg)[2]



#Time series
ggplot(df_graphic, aes(x=ymd(endDate), y=hitCount)) +
  geom_point() +
  geom_smooth(color='black', fill='pink', size=0.1) +
  xlab('') + ylab('') +
  theme_minimal()

filestub <- paste('Post count time series -', country, keyword)
filename <- paste0(dir, filestub, '.png') 
ggsave(filename, w=8, h=6)

ggplot(df_graphic, aes(x=ymd(endDate), y=reac_total)) +
  geom_point() +
  geom_smooth(color='black', fill='pink', size=0.1) +
  xlab('') + ylab('') +
  theme_minimal()

filestub <- paste('Post reac time series -', country, keyword)
filename <- paste0(dir, filestub, '.png') 
ggsave(filename, w=8, h=6)


