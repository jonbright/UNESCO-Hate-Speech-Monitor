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

#for testing
#df <- read_excel('bigram collocations.xlsx')

df$bigram <- factor(df$bigram)
df$bigram <- fct_reorder(df$bigram, df$keyword, min)

dfb <- df[df$keyword==keyword,]

ggplot(dfb, aes(x=bigram, y=score, fill=keyword)) +
  geom_bar(stat='identity') +
  coord_flip() +
  theme_minimal() +
  ylab('Likelihood ratio') +
  xlab('') +
  scale_fill_discrete('')

filestub <- paste('Collocations - ', country, keyword)
filename <- paste0(dir, filestub, '.png') 
ggsave(filename, w=8, h=6)

