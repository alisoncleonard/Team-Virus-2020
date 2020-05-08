install.packages("ggplot2") #plotting
install.packages("dplyr") #data maagement
install.packages("RColorBrewer") #color scheme
install.packages("gganimate") #animate plots
install.packages("gifski") #saving gif
install.packages("av") 
install.packages('cowplot') #for plotting multiple graphs in a grid 
install.packages('ggpubr') #for plotting multiple graphs in a grid 
#install.packages("viridis")      #from R-graph-gallery (for appearance)
#install.packages("hrbrthemes")   #from R-graph-gallery (for appearance)


library(ggplot2)
library(dplyr)
library(RColorBrewer)
library(gganimate)
library(gifski)
library(av)
library(cowplot)
library(ggpubr)
#library(viridis)     #from R-graph-gallery (for appearance)
#library(hrbrthemes)  #from R-graph-gallery (for appearance)

#Directory where data is located
setwd("/Users/adamdziulko/Documents/Boulder-y1/Rotations/Team\ Virus/git/mesa_data/")

# Specify the prefix of your file
prefix <- "VirusModel_"

#Read in cvs file
data1 <- read.table(paste0(prefix, "lowmob_highfrac_1.csv"),
                    sep = ",",
                    header = TRUE)
data2 <- read.table(paste0(prefix, "lowmob_highfrac.csv"),
                    sep = ",",
                    header = TRUE)
data3 <- read.table(paste0(prefix, "lowmob_lowfrac_1.csv"),
                    sep = ",",
                    header = TRUE)
data4 <- read.table(paste0(prefix, "lowmob_lowfrac.csv"),
                    sep = ",",
                    header = TRUE)
#remove unncessary column
data1 = data1[,c(-1)]
data2 = data2[,c(-1)]
data3 = data3[,c(-1)]
data4 = data4[,c(-1)]
#combine replicate data frames
highfrac_data = rbind(data1, data2)
lowfrac_data = rbind(data3, data4)

#identify different parameter combinations
high_lvl = unique(highfrac_data$Model.Params)
low_lvl = unique(lowfrac_data$Model.Params)
#output first 5 combinations
high_lvl[1:5]

#Calculate mean/sd/se values of replicate iterations of high-fraction symptomatic
high_mean = highfrac_data %>% group_by(Step, Model.Params) %>% summarise(susceptible_mean = mean(Susceptible),
                                                                exposed_mean = mean(Exposed), 
                                                                infectious_mean = mean(Infectious),
                                                                infectious_sd = sd(Infectious),
                                                                recovered_mean = mean(Recovered),
                                                                dead_mean = mean(Dead),
                                                                dead_sd = sd(Dead),
                                                                number_iterations = n()) %>%
          mutate(infectious_se = infectious_sd / sqrt(number_iterations), 
                dead_se = dead_sd / sqrt(number_iterations)) #Calculate standard error for 'Infectious' data

#Calculate mean/sd/se values of replicate iterations of low-fraction symptomatic
low_mean = lowfrac_data %>% group_by(Step, Model.Params) %>% summarise(susceptible_mean = mean(Susceptible),
                                                                exposed_mean = mean(Exposed), 
                                                                infectious_mean = mean(Infectious),
                                                                infectious_sd = sd(Infectious),
                                                                recovered_mean = mean(Recovered),
                                                                dead_mean = mean(Dead),
                                                                dead_sd = sd(Dead),
                                                                number_iterations = n()) %>%
          mutate(infectious_se = infectious_sd / sqrt(number_iterations), 
                dead_se = dead_sd / sqrt(number_iterations)) #Calculate standard error for 'Infectious' data





#create vector of even numbers (for removing either all small or large grid sizes)
evens <- seq(2, length(high_lvl), 2)

#filter paramter combinations of large and small grid sizes for high-fraction symtomatic data
filt_high_lvl <-  high_lvl[-evens]
large_filt_high_lvl = filt_high_lvl[c(-1, -2, -3, -4, -9, -10, -11, -12, -17, -18, -19, -20, -25, -26, -27, -28,
                                -33, -34, -35, -36, -41, -42, -43, -44)]

small_filt_high_lvl = filt_low_lvl[c(-5, -6, -7, -8, -13, -14, -15, -16, -21, -22, -23, -24, -29, -30, -31, -32,
                                -37, -38, -39, -40, -45, -46, -47, -48)]



#filter paramter combinations of large and small grid sizes for low-fraction symtomatic data
filt_low_lvl = low_lvl[-evens]
large_filt_low_lvl = filt_low_lvl[c(-1, -2, -3, -4, -9, -10, -11, -12, -17, -18, -19, -20, -25, -26, -27, -28,
                                -33, -34, -35, -36, -41, -42, -43, -44)]

small_filt_low_lvl = filt_low_lvl[c(-5, -6, -7, -8, -13, -14, -15, -16, -21, -22, -23, -24, -29, -30, -31, -32,
                              -37, -38, -39, -40, -45, -46, -47, -48)]





#save plot as pdf (used to make single graphs looking at combination parameters for #dead&infectious in large grid/high-frac symp)
pdf(file = paste0(prefix, "_infectious_dead_line_21.24.pdf"), width = 16, height = 12)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[21:24])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  #geom_point() + ###(can use this to specify points being graphed)
  #geom_ribbon(aes(x = Step, 
   #               ymin=dead_mean - dead_se, 
    #              ymax=dead_mean + dead_se), 
     #             linetype=2, alpha=0.1, color='black', fill="black") + ###(can use this to plot standard error)
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  #geom_point() + 
 # geom_ribbon(aes(x = Step, 
  #                ymin=infectious_mean - infectious_se, 
   #               ymax=infectious_mean + infectious_se, color =Model.Params, fill=Model.Params), 
    #              linetype=2, alpha=0.1) +
  coord_cartesian(xlim = c(0, 105)) + ###(used to limit x-axis)
  # Plot title
  ggtitle("Infectious Over Time") +
  # Axes names
  labs(x = "# Ticks", y = "# Infectious") 
# Save plot
dev.off()





####DEAD GRAPH
#save plot as pdf
pdf(file = paste0(prefix, "_dead_line_21.24.pdf"), width = 16, height = 12)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
ggplot(data = high_mean %>% filter(Model.Params %in% filt_high_lvl[21:24])) +
  #line for param1
    geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
              size=1) +
  #geom_point() + 
  #geom_ribbon(aes(x = Step, 
  #               ymin=dead_mean - dead_se, 
  #              ymax=dead_mean + dead_se), 
  #             linetype=2, alpha=0.1, color='black', fill="black") +
  coord_cartesian(xlim = c(0, 105)) +
  # Plot title
  ggtitle("Dead Over Time") +
  # Axes names
  labs(x = "# Ticks", y = "# Dead") 
# Save plot
dev.off()




######multigird (Large pop, High fraction symptomatic)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
a = ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[1:4])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  coord_cartesian(xlim = c(0, 105)) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

b = ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[5:8])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  coord_cartesian(xlim = c(0, 105)) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

c = ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[9:12])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  coord_cartesian(xlim = c(0, 105)) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

d = ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[13:16])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  coord_cartesian(xlim = c(0, 105)) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

e = ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[17:20])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  coord_cartesian(xlim = c(0, 105)) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

f = ggplot(data = high_mean %>% filter(Model.Params %in% large_filt_high_lvl[21:24])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  coord_cartesian(xlim = c(0, 105)) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 
#Code for saving plot in grid as pdf
figure = ggarrange(a, b, c, d, e, f, labels = c("A", "B", "C", "D", "E", "F"), ncol = 2, nrow = 3)
pdf(file = paste0(prefix, "_infectious_dead_all_highfrac_largepop.pdf"), width = 36, height = 24)
figure
dev.off()




####
######multigird (Large pop, Low fraction symptomatic)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
aa = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[1:4])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 100)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 120)) +       # set y axis limits
  theme(text = element_text(size = 16),) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

bb = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[5:8])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 100)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 120)) +       # set y axis limits
  theme(text = element_text(size = 16),) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

cc = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[9:12])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 100)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 120)) +       # set y axis limits
  theme(text = element_text(size = 16),) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

dd = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[13:16])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 100)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 120)) +       # set y axis limits
  theme(text = element_text(size = 16),) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

ee = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[17:20])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 100)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 120)) +       # set y axis limits
  theme(text = element_text(size = 16),) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

ff = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[21:24])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 100)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 120)) +       # set y axis limits
  theme(text = element_text(size = 16),) +
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 
#Code for saving plot in grid as pdf
figure = ggarrange(aa, bb, cc, dd, ee, ff, labels = c("A", "B", "C", "D", "E", "F"), ncol = 2, nrow = 3)
pdf(file = paste0(prefix, "_infectious_dead_all_lowfrac_largepop_coord.pdf"), width = 36, height = 24)
figure
dev.off()

######






####
######multigird (Small pop, Low fraction symptomatic)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
aaa = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[1:4])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 310)) +       # set y axis limits
  theme(text = element_text(size = 16),) + 
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

bbb = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[5:8])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 310)) +       # set y axis limits
  theme(text = element_text(size = 16),) + 
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

ccc = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[9:12])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 310)) +       # set y axis limits
  theme(text = element_text(size = 16),) + 
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

ddd = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[13:16])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 310)) +       # set y axis limits
  theme(text = element_text(size = 16),) + 
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

eee = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[17:20])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 310)) +       # set y axis limits
  theme(text = element_text(size = 16),) + 
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 

fff = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[21:24])) +
  geom_line(aes(x = Step, y = dead_mean, group=Model.Params, color=Model.Params), 
            size=1, linetype=2) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=1) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 310)) +       # set y axis limits
  theme(text = element_text(size = 16),) + 
  # Axes names
  labs(x = "Time", y = "# Infectious and Dead") 
#Code for saving plot in grid as pdf
figure = ggarrange(aaa, bbb, ccc, ddd, eee, fff, labels = c("A", "B", "C", "D", "E", "F"), ncol = 2, nrow = 3)
pdf(file = paste0(prefix, "_infectious_dead_all_lowfrac_smallpoptest.pdf"), width = 36, height = 24)
figure
dev.off()


######






##########################################PLOTS FOR PRESENTATION
####
######multigird (Small pop, Low fraction symptomatic, changing initial fraction recovered)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
aaaa = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[1:4])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 150)) +       # set y axis limits
  theme(text = element_text(size = 26), legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank())   

bbbb = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[5:8])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 150)) +       # set y axis limits
  theme(text = element_text(size = 26), legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank())  

cccc = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[9:12])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 150)) +       # set y axis limits
  theme(text = element_text(size = 26), legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank()) 
#Code for saving plot in grid as pdf
figure = ggarrange(aaaa, bbbb, cccc, labels = c("A", "B", "C"), ncol = 3, nrow = 1)
pdf(file = paste0(prefix, "_infectious_dead_initialfractionrecovered_lowfrac_smallpoptest.pdf"), width = 44, height = 14)
figure
dev.off()
######





####
######multigird (low-frac symptomatic, .1 init frac recoverd, changing high vs low population)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
small_grid = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[5:8])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 105)) +       # set y axis limits
  theme(text = element_text(size = 26),legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank())  

large_grid = ggplot(data = low_mean %>% filter(Model.Params %in% large_filt_low_lvl[5:8])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 105)) +       # set y axis limits
  theme(text = element_text(size = 26),legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank())  
#Code for saving plot in grid as pdf
figure = ggarrange(small_grid, large_grid, labels = c("A", "B"), ncol = 2, nrow = 1)
pdf(file = paste0(prefix, "_infectious_dead_1intitfrac_lowfrac_smallvslargegrid.pdf"), width = 44, height = 14)
figure
dev.off()


######







####
######multigird (Small pop, .1 init frac recoverd, changing high-frac and low-frac symptomatic)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
low_frac = ggplot(data = low_mean %>% filter(Model.Params %in% small_filt_low_lvl[5:8])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 150)) +       # set y axis limits
  theme(text = element_text(size = 26),legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank())  

high_frac = ggplot(data = high_mean %>% filter(Model.Params %in% small_filt_high_lvl[5:8])) +
  geom_line(aes(x = Step, y = infectious_mean, group=Model.Params, color=Model.Params), 
            size=3) +
  theme_classic() +
  scale_x_continuous(expand = c(0, 0), limits = c(0, 410)) +     # set x axis limits
  scale_y_continuous(expand = c(0, 0), limits = c(0, 150)) +       # set y axis limits
  theme(text = element_text(size = 26),legend.position = "none", axis.title.x = element_blank(), 
        axis.title.y = element_blank())  
#Code for saving plot in grid as pdf
figure = ggarrange(low_frac, high_frac, labels = c("A", "B"), ncol = 2, nrow = 1)
pdf(file = paste0(prefix, "_infectious_dead_1intitfrac_smallpop_lowfrachighfrac.pdf"), width = 44, height = 14)
figure
dev.off()


######



























































####start of trying to make washington post graphs (stacked area chart)
#subset data to agent types
summarise_sub_1 = mean_param_1[,c(-5,-8, -9, -10, -11 )]
summarise_sub_2 = mean_param_2[,c(-5,-8, -9, -10, -11 )]
summarise_sub_3 = mean_param_3[,c(-5,-8, -9, -10, -11 )]
summarise_sub_4 = mean_param_4[,c(-5,-8, -9, -10, -11 )]
# Compute percentages with dplyr
agent_percentage <- summarise_sub_1  %>%
  group_by(Step) %>%
  summarise(n = sum(value)) %>%
  mutate(percentage = n / sum(n))

#further subset data and prepare for rbind
sum_sub_sus_1 = summarise_sub_1[,c(-3, -4, -5, -6)]
sum_sub_sus_1['agent'] = 'susceptible'
colnames(sum_sub_sus_1) = c("Step", "number", "agent")

sum_sub_inf_1 = summarise_sub_1[,c(-3, -2, -5, -6)]
sum_sub_inf_1['agent'] = 'infectious'
colnames(sum_sub_inf_1) = c("Step", "number", "agent")

sum_sub_exp_1 = summarise_sub_1[,c(-2, -4, -5, -6)]
sum_sub_exp_1['agent'] = 'exposed'
colnames(sum_sub_exp_1) = c("Step", "number", "agent")

sum_sub_dead_1 = summarise_sub_1[,c(-3, -2, -5, -4)]
sum_sub_dead_1['agent'] = 'dead'
colnames(sum_sub_dead_1) = c("Step", "number", "agent")

sum_sub_rec_1 = summarise_sub_1[,c(-3, -2, -4, -6)]
sum_sub_rec_1['agent'] = 'recovered'
colnames(sum_sub_rec_1) = c("Step", "number", "agent")

#merge all above
z_merged = rbind(sum_sub_sus_1, sum_sub_inf_1, sum_sub_exp_1, sum_sub_dead_1, sum_sub_rec_1)

# Compute percentages with dplyr
agent_percentage <- z_merged  %>%
  group_by(Step, agent) %>%
  summarise(n = sum(number)) %>%
  mutate(percentage = n / sum(n))

#plot and save as gif
gif_plot = ggplot(agent_percentage, aes(x=Step, y=percentage, fill=agent)) + 
  geom_area(alpha=0.6 , size=1, colour="black") + 
  transition_reveal(Step) 
#save as gif
animate(gif_plot, duration = 5, fps = 20, width = 200, height = 200, renderer = gifski_renderer())
anim_save("test.gif")


#plot normal (no animation)
pdf(file = paste0(prefix, "_stacked_area.pdf"), width = 24, height = 12)
#plot
ggplot(agent_percentage, aes(x=Step, y=percentage, fill=agent)) + 
  geom_area(alpha=0.6 , size=1, colour="black")

# Save plot
dev.off()

