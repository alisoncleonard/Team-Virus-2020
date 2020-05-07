install.packages("ggplot2")
install.packages("dplyr")
install.packages("RColorBrewer")
install.packages("gganimate")
install.packages("gifski")
install.packages("av")
#install.packages("viridis")      #from R-graph-gallery (for appearance)
#install.packages("hrbrthemes")   #from R-graph-gallery (for appearance)


library(ggplot2)
library(dplyr)
library(RColorBrewer)
library(gganimate)
library(gifski)
library(av)
#library(viridis)     #from R-graph-gallery (for appearance)
#library(hrbrthemes)  #from R-graph-gallery (for appearance)

#Directory where data is located
setwd("/Users/adamdziulko/Documents/Boulder-y1/Rotations/Team\ Virus/git/")

# Specify the prefix of your file
prefix <- "VirusModel_Step_Data"

#Read in cvs file
data <- read.table(paste0(prefix, "_alison.csv"),
                   sep = ",",
                   header = TRUE)
#remove unncessary column
data = data[,c(-1)]

#identify different parameters
lvl = unique(data$Model.Params)
lvl
#subset data by parameter
param_1 <- subset(data, lvl[1] == Model.Params)
param_2 <- subset(data, lvl[2] == Model.Params)
param_3 <- subset(data, lvl[3] == Model.Params)
param_4 <- subset(data, lvl[4] == Model.Params)

#Get mean and standard deviation of x-iteration parameters (focused on 'Infectious' data, but can focus on all)
z = 1.96 # 95% confidence interval (can change )
for (i in 1:nlevels(lvl)) {
  param_i = eval(parse(text = paste0("param_",i)))
  mean_param_i = paste("mean_param_", i, sep = "")
  assign(mean_param_i, param_i %>% group_by(Step) %>% summarise(susceptible_mean = mean(Susceptible),
                                                            exposed_mean = mean(Exposed), 
                                                            infectious_mean = mean(Infectious),
                                                            infectious_sd = sd(Infectious),
                                                            recovered_mean = mean(Recovered),
                                                            dead_mean = mean(Dead),
                                                            number_iterations = n()) %>%
           mutate(infectious_se = infectious_sd / sqrt(number_iterations), #Calculate standard error for 'Infectious' data
           inf_lower_ci = infectious_mean - (z * infectious_se / sqrt(number_iterations)), #Calculate lower confidence interval for 'Infectious' data
           inf_upper_ci = infectious_mean + (z * infectious_se / sqrt(number_iterations)))) #Calculate upper confidence interval for 'Infectious' data
}



#save plot as pdf
pdf(file = paste0(prefix, "_infectious_line.pdf"), width = 24, height = 12)
## Tell ggplot to plot Step on the x-axis and mean Infectious on the y-axis
ggplot() +
  #line for param1
  geom_line(data = mean_param_1, aes(x = Step, y = infectious_mean), size=1, color="black") +
  geom_point() + 
  geom_ribbon(aes(x =mean_param_1$Step, 
                  ymin=mean_param_1$inf_lower_ci, 
                  ymax=mean_param_1$inf_upper_ci), 
                  linetype=2, alpha=0.1, color='black', fill="black") +
  #line for param2
  geom_line(data = mean_param_2, aes(x = Step, y = infectious_mean), size=1, color="red") +
  geom_point() + 
  geom_ribbon(aes(x =mean_param_2$Step, 
                  ymin=mean_param_2$inf_lower_ci, 
                  ymax=mean_param_2$inf_upper_ci), 
                  linetype=2, alpha=0.1, color="red", fill="red") +
  #line for param3
  geom_line(data = mean_param_3, aes(x = Step, y = infectious_mean), size=1, color="green") +
  geom_point() + 
  geom_ribbon(aes(x =mean_param_3$Step, 
                  ymin=mean_param_3$inf_lower_ci, 
                  ymax=mean_param_3$inf_upper_ci), 
                  linetype=2, alpha=0.1, color="green", fill="green") +
  #line for param3
  geom_line(data = mean_param_4, aes(x = Step, y = infectious_mean), size=1, color="blue") +
  geom_point() + 
  geom_ribbon(aes(x =mean_param_4$Step, 
                  ymin=mean_param_4$inf_lower_ci, 
                  ymax=mean_param_4$inf_upper_ci), 
                  linetype=2, alpha=0.1, color="blue", fill="blue") + 
  #Legend (never got legend to show up, might not need if using R-graph-gallery)
  

  # Plot title
  ggtitle("Infectious Over Time") +
  # Axes names
  labs(x = "# Ticks", y = "# Infectious") 

  # Options to adjust the size and placement (hjust & vjust) of your labels (haven't played around with this yet, but this is backbone)
  #theme(plot.title = element_text(size = 25, hjust = 0.5),
  #      axis.title.x = element_text(size = 20, hjust = 0.5, vjust = 0.5),
  #      axis.text.x = element_text(size = 15, hjust = 0.5, vjust = 0.5),
  #      axis.title.y = element_text(size = 20, hjust = 0.5, vjust = 0.5),
  #      axis.text.y = element_text(size = 15, hjust = 0.5, vjust = 0.5)) +
  
# Save plot
dev.off()



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

