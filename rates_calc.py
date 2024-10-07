Salary = 12000
Days = 20

Hours_p_month = Days*8
Minutes_p_month = Days*60*8

RatePerMin = Salary/Minutes_p_month
RatePerHour = Salary/Hours_p_month

print(RatePerMin)
print(RatePerHour)

VOCMax_Saving = 5*20
RateSave = VOCMax_Saving*RatePerMin
print(RateSave)