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
graphicsdir <- args[3]
datadir <- args[4]
df <- read_excel(data_file_name)

#read your own df here for testing
#dir <- ''
#df <- read_excel('haiti time series.xlsx')

df$endDate <- ymd(df$endDate)
current_date <- max(df$endDate)


#Overall summary graphics ----
df$reac_total <- rowSums(df[9:17])
df_overall <- 
  df %>%
  group_by(endDate) %>%
  summarise(
    hitCount = sum(hitCount),
    shareCount = sum(shareCount),
    likeCount = sum(likeCount),
    sadCount = sum(sadCount),
    angryCount = sum(angryCount),
    loveCount = sum(loveCount),
    careCount = sum(careCount),
    wowCount = sum(wowCount),
    hahaCount = sum(hahaCount),
    commentCount = sum(commentCount),
    reac_count = sum(reac_total),
  ) %>% 
  pivot_longer(!endDate, names_to='measure', values_to='value')
  

df_overall_hist <- df_overall[df_overall$endDate!=current_date,]
df_overall_curr <- df_overall[df_overall$endDate==current_date,]


#create historical means and confidence intervals for each variable
#warnings come from ci about default class
hist_means <- 
  df_overall_hist %>%
  group_by(measure) %>%
  summarise(
    hist_mean = mean(value),
    lowCI = ci(value)[2],
    hiCI = ci(value)[3]
  )

df_overall_curr <- left_join(df_overall_curr, hist_means, by='measure')
df_overall_curr$interpretation <- 
  case_when(
    df_overall_curr$value < df_overall_curr$lowCI ~ 'lower than average',
    df_overall_curr$value > df_overall_curr$hiCI ~ 'higher than average',
    TRUE ~ 'about average'
  )

#hard assign colour
df_overall_curr$col <- 
  case_when(
    df_overall_curr$value < df_overall_curr$lowCI ~ '#4CAF50',
    df_overall_curr$value > df_overall_curr$hiCI ~ '#E64819',
    TRUE ~ '#FFA000'
  )

df_overall_curr$label <- 
  case_when(
    df_overall_curr$measure=='hitCount' ~ 'Num. Posts:\n', 
    df_overall_curr$measure=='shareCount' ~ 'Num. Shares:\n',
    df_overall_curr$measure=='reac_count' ~ 'Num. Reactions:\n',
    df_overall_curr$measure=='likeCount' ~ 'Num. Likes:\n',
    df_overall_curr$measure=='sadCount' ~ 'Num. Sads:\n',
    df_overall_curr$measure=='angryCount' ~ 'Num. Angries:\n',
    df_overall_curr$measure=='loveCount' ~ 'Num. Loves:\n',
    df_overall_curr$measure=='careCount' ~ 'Num. Cares:\n',
    df_overall_curr$measure=='wowCount' ~ 'Num. Wows:\n',
    df_overall_curr$measure=='hahaCount' ~ 'Num. Hahas:\n',
    df_overall_curr$measure=='commentCount' ~ 'Num. Comments:\n'
  )

df_overall_curr$label <- paste0(df_overall_curr$label, df_overall_curr$interpretation)



#df_overall_curr$label <- as.list(expression(df_overall_curr$label~italic(df_overall_curr$interpretation)))

df_overall_basic <- df_overall_curr[df_overall_curr$measure %in% c('hitCount', 'shareCount', 'reac_count'),]


df_overall_detailed <- df_overall_curr[df_overall_curr$measure %in% c('likeCount', 'sadCount', 'angryCount',
                                                                      'loveCount', 'careCount', 'wowCount',
                                                                      'hahaCount'),]


ggplot() +
  geom_bar(data=df_overall_basic, aes(x=label, y=value), stat='identity', color='black', 
           fill=df_overall_basic$col[order(df_overall_basic$label)]) + 
  geom_point(data=df_overall_basic, aes(x=label, y=hist_mean)) +
  geom_errorbar(data=df_overall_basic, aes(x=label, y=hist_mean, ymin=lowCI, ymax=hiCI)) +
  facet_wrap(~measure, scales='free', ncol=1) +
  theme_minimal() +
  coord_flip() +
  xlab('') + ylab('') +
  labs(tag = "arbitrary words") +
  theme(strip.text.x = element_blank(), plot.tag.position = c(0.5, -1)) +
  scale_y_continuous(labels=scales::comma_format()) 

#Save out the image and accompanying data
filestub <- paste('Basic_Summary_Statistics', country)
filename <- paste0(graphicsdir, filestub, '.png') 
ggsave(filename, w=8, h=6)
filename <- paste0(datadir, filestub, '.csv') 
write.csv(df_overall_basic, filename)

ggplot() +
  geom_bar(data=df_overall_detailed, aes(x=label, y=value), stat='identity', 
           fill=df_overall_detailed$col[order(df_overall_detailed$label)]) + 
  geom_point(data=df_overall_detailed, aes(x=label, y=hist_mean)) +
  geom_errorbar(data=df_overall_detailed, aes(x=label, y=hist_mean, ymin=lowCI, ymax=hiCI)) +
  facet_wrap(~measure, scales='free', ncol=1) +
  theme_minimal() +
  coord_flip() +
  xlab('') + ylab('') +
  labs(tag = "arbitrary words") +
  theme(strip.text.x = element_blank(), plot.tag.position = c(0.5, -1)) +
  scale_y_continuous(labels=scales::comma_format())


filestub <- paste('Detailed_Summary_Statistics', country)
filename <- paste0(graphicsdir, filestub, '.png') 
ggsave(filename, w=8, h=6)
filename <- paste0(datadir, filestub, '.csv') 
write.csv(df_overall_detailed, filename)


#Keyword summary graphics ----
#this basically just pivots it longer
#but reusing the above code saved me having to type out the reac names again
df_overall_kw <- 
  df %>%
  group_by(endDate, searched_keyword) %>%
  summarise(
    hitCount = sum(hitCount),
    shareCount = sum(shareCount),
    likeCount = sum(likeCount),
    sadCount = sum(sadCount),
    angryCount = sum(angryCount),
    loveCount = sum(loveCount),
    careCount = sum(careCount),
    wowCount = sum(wowCount),
    hahaCount = sum(hahaCount),
    commentCount = sum(commentCount),
    reac_count = sum(reac_total),
  ) %>% 
  pivot_longer(!c(endDate, searched_keyword), names_to='measure', values_to='value')

df_overall_hist_kw <- df_overall_kw[df_overall_kw$endDate!=current_date,]
df_overall_curr_kw <- df_overall_kw[df_overall_kw$endDate==current_date,]


#create historical means and confidence intervals for each variable
#warnings come from ci about default class
hist_means_kw <- 
  df_overall_hist_kw %>%
  group_by(measure, searched_keyword) %>%
  summarise(
    hist_mean = mean(value),
    lowCI = ci(value)[2],
    hiCI = ci(value)[3],
    low25  = percent_rank(0.025),
    hi975  = quantile(value, 0.975)
    
  )



df_overall_curr <- left_join(df_overall_curr_kw, hist_means_kw, by=c('measure', 'searched_keyword'))
df_overall_curr$interpretation <- 
  case_when(
    df_overall_curr$value < df_overall_curr$lowCI ~ 'lower than average',
    df_overall_curr$value > df_overall_curr$hiCI ~ 'higher than average',
    TRUE ~ 'about average'
  )

#hard assign colour
df_overall_curr$col <- 
  case_when(
    df_overall_curr$value < df_overall_curr$lowCI ~ '#4CAF50',
    df_overall_curr$value > df_overall_curr$hiCI ~ '#E64819',
    TRUE ~ '#FFA000'
  )

df_overall_curr$label <- 
  case_when(
    df_overall_curr$measure=='hitCount' ~ 'Num. Posts:\n', 
    df_overall_curr$measure=='shareCount' ~ 'Num. Shares:\n',
    df_overall_curr$measure=='reac_count' ~ 'Num. Reactions:\n',
    df_overall_curr$measure=='likeCount' ~ 'Num. Likes:\n',
    df_overall_curr$measure=='sadCount' ~ 'Num. Sads:\n',
    df_overall_curr$measure=='angryCount' ~ 'Num. Angries:\n',
    df_overall_curr$measure=='loveCount' ~ 'Num. Loves:\n',
    df_overall_curr$measure=='careCount' ~ 'Num. Cares:\n',
    df_overall_curr$measure=='wowCount' ~ 'Num. Wows:\n',
    df_overall_curr$measure=='hahaCount' ~ 'Num. Hahas:\n',
    df_overall_curr$measure=='commentCount' ~ 'Num. Comments:\n'
  )

df_overall_curr$label <- paste0(df_overall_curr$label, df_overall_curr$interpretation)

kw_counts <- df_overall_curr[df_overall_curr$measure=='hitCount',]
kw_counts$searched_keyword <- factor(kw_counts$searched_keyword)

ggplot() +
  geom_bar(data=kw_counts, aes(x=searched_keyword, y=value), stat='identity', color='black', 
           fill=kw_counts$col[order(kw_counts$searched_keyword)]) + 
  geom_point(data=kw_counts, aes(x=searched_keyword, y=hist_mean)) +
  geom_errorbar(data=kw_counts, aes(x=searched_keyword, y=hist_mean, ymin=lowCI, ymax=hiCI)) +
  theme_minimal() +
  scale_x_discrete(limits = rev(levels(kw_counts$searched_keyword))) +
  coord_flip() +
  xlab('') + ylab('') +
  labs(tag = "arbitrary words") +
  theme(strip.text.x = element_blank(), plot.tag.position = c(0.5, -1)) +
  scale_y_continuous(labels=scales::comma_format()) 
  
#scale_fill_manual(values=c('red', 'red', 'red')) 
#scale_fill_manual(values=col) 

filestub <- paste('Basic_Summary_Statistics_per_Keyword', country)
filename <- paste0(graphicsdir, filestub, '.png') 
ggsave(filename, w=8, h=10)
filename <- paste0(datadir, filestub, '.csv') 
write.csv(kw_counts, filename)

kw_counts <- df_overall_curr[df_overall_curr$measure=='reac_count',]
kw_counts$searched_keyword <- factor(kw_counts$searched_keyword)

ggplot() +
  geom_bar(data=kw_counts, aes(x=searched_keyword, y=value), stat='identity', color='black', 
           fill=kw_counts$col[order(kw_counts$searched_keyword)]) + 
  geom_point(data=kw_counts, aes(x=searched_keyword, y=hist_mean)) +
  geom_errorbar(data=kw_counts, aes(x=searched_keyword, y=hist_mean, ymin=lowCI, ymax=hiCI)) +
  theme_minimal() +
  scale_x_discrete(limits = rev(levels(kw_counts$searched_keyword))) +
  coord_flip() +
  xlab('') + ylab('') +
  labs(tag = "arbitrary words") +
  theme(strip.text.x = element_blank(), plot.tag.position = c(0.5, -1)) +
  scale_y_continuous(labels=scales::comma_format()) 

#scale_fill_manual(values=c('red', 'red', 'red')) 
#scale_fill_manual(values=col) 

filestub <- paste('Basic_Reaction_Statistics_per_Keyword', country)
filename <- paste0(graphicsdir, filestub, '.png') 
ggsave(filename, w=8, h=10)


#write out meta file? ----




