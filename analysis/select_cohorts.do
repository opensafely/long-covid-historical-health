use output/input.dta, clear

* Dates
foreach variable in sgss_positive primary_care_covid hospital_covid {
    rename `variable' `variable'_temp
    gen `variable'= date(`variable'_temp,"YMD")
    drop `variable'_temp
}
gen first_covid = min(sgss_positive, primary_care_covid, hospital_covid)

preserve
keep if first_covid <= date("2020-05-01", "YMD")
save output/input_before_may.dta, replace
restore

keep if first_covid > date("2020-05-01", "YMD")
save output/input_after_may.dta, replace
