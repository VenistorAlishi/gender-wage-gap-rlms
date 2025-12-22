***Выберите зависимую переменную. 
***Определите целевые и контрольные переменные. 
***Обсудите возможные источники смещения оценок. 
***Запишите базовую модель. 
***Определите множество возможных альтернативных моделей, включающих дополнительные переменные. 

***Оцените базовую модель и предполагаемые альтернативы. 

**Визуальный анализ: графики
*Диаграмма рассеяния и линия регрессии
twoway (scatter earnings height if sex==0, color(red)) (scatter earnings height if sex==1, color(blue))|| lfit earnings height|| lowess earnings height, name(graph1, replace)

twoway hist earnings if sex==1, percent name(graph7, replace)  
twoway hist earnings if sex==0, percent name(graph8, replace) 

graph bar earnings, over(sex) name(graph6, replace)
graph bar earnings, over(cworker) name(graph5, replace)

hist earnings, normal
histogram earnings, kdensity normal


**Описательные статистики
sum
*!!! по категориям переменной black строим описательные статистики переменной ed
tab sex, sum(earnings)
tab cworker, sum(earnings)


**Корреляционная матрица
pwcorr earnings height sex age educ, sig obs star(.05) 


*Оценивание регрессий
reg earnings height sex age educ 
est store a
*outreg2 using "C:\Users\57563\Documents\myfile.xls", excel replace
*outreg2 using "C:\Users\57563\Documents\myfile.xls", adds(joint, r(estimate), t-stat, `tstat', p-val,`pval') replace see

reg earnings sex age educ 
est store b

gen age2=(age)^2

reg earnings sex age age2 educ 
est store c

gen learnings=ln(earnings)
gen lheight=ln(height)

reg learnings sex age age2 educ 
est store d

*Сопоставление результатов оценивания разных регрессий
est tab a b c d, se p stats(N r2 r2_a aic bic) 
est tab a b c d, stats(N r2 r2_a aic bic) star(.1 .05 .01)


***Проверьте чувствительность, качество подгонки данных моделью, соответствие предпосылкам теоремы Гаусса-Маркова. Выберите лучшую модель. Сформулируйте выводы.


reg learnings sex age age2 educ i.cworker
est store e

**Теорема Гаусса – Маркова для случая множественной линейной регрессии
**Если модель множественной линейной регрессии 
**1) Правильно  специфицирована

*Тест Бокса-Кокса (см. help boxcox)
boxcox earnings height  , model(theta) lrtest

boxcox earnings  , notrans(age age2 sex educ) model(lhsonly) lrtest

boxcox bpdiast bmi tcresult age sex, model(lhsonly) lrtest nolog nologlr
boxcox bpdiast bmi tcresult, notrans(sex age) model(rhsonly) lrtest nolog nologlr

*Тест Рамсея
estat ovtest
*estat ovtest performs two versions of the Ramsey (1969) regression specification-error test (RESET) for omitted variables.  This test amounts to *fitting y=xb+zt+u and then testing t=0.  If the rhs option is not specified, powers of the fitted values
*are used for z.  If rhs is specified, powers of the individual elements of x are used.

*Тест Чоу (если подозреваем наличие структурного сдвига)
/* chow test of walk*/
quietly reg VRP Lсреднегодоваячисленностьзаня KстоимостьОсновныхфондов AУРОВЕНЬИННОВАЦИОННОЙАКТИВНОС Dm
est store reg1
  scalar rss_rm=e(rss)
  scalar df_rm=e(df_r)

quietly reg price_msq dist kitsp livesp metrdist if walk==1
est store reg_walk1
  scalar rss_walk1=e(rss)
  scalar df_walk1=e(df_r)

quietly reg price_msq dist kitsp livesp metrdist if walk!=1
est store reg_walk0
  scalar rss_walk0=e(rss)
  scalar df_walk0=e(df_r)

est tab reg1 reg_walk1 reg_walk0, stats( N rss r2) star(.01, .05, .1)

  scalar fchow_walk=((rss_rm-(rss_walk1+rss_walk0))/(df_rm-(df_walk1+df_walk0)))/((rss_walk1+rss_walk0)/(df_walk1+df_walk0))
  scalar pval_chow_walk=Ftail(df_rm-(df_walk1+df_walk0), df_walk1+df_walk0, fchow_walk)

 scalar list rss_walk1 rss_walk0 rss_rm
 scalar list df_walk1 df_walk0 df_rm
 scalar list fchow_walk
 scalar list pval_chow_walk
*********

**2) Не существует линейной связи между регрессорами
vif
**3) Возмущения имеют нулевое мат. ожидание E(ui) = 0, 
**4) Дисперсии возмущений одинаковы D(uj) = σu2 , j = 1,…,n
hettest

reg learnings lheight age age2 educ, vce(robust) 

****создаем переменную остатков, проводим тест на нормальность
predict resid, stdp
sktest resid
****

*или
estat szroeter

*если есть гетероскедастичность, то выполняем коррекцию стандартных ошибок
reg VRP Lсреднегодоваячисленностьзаня KстоимостьОсновныхфондов AУРОВЕНЬИННОВАЦИОННОЙАКТИВНОС Dm, vce(robust)

**5) Возмущения с разными номерами не коррелируют Cov(ui, uj) = 0 
**Тогда оценки МНК являются BLUE (Best Linear Unbiased Estimator). 
















