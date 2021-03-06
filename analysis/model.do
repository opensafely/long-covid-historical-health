global projectdir `c(pwd)'
di "$projectdir"
global population `1'

use output/input$population.dta, clear

egen comorbidities = rowtotal(diabetes cancer haem_cancer asthma ///
    chronic_respiratory_disease chronic_cardiac_disease chronic_liver_disease ///
    stroke_or_dementia other_neuro organ_transplant dysplenia ra_sle_psoriasis ///
    other_immunosup_cond)
recode comorbidities 2/max = 2

local exposures sex ///
    age_group ///
    ethnicity ///
    imd ///
    comorbidities ///
    mental_health ///
    bmi ///
    diabetes ///
    asthma

global model_1 i.age_group
global model_2 i.age_group i.sex
global model_3 i.age_group i.sex i.ethnicity
global model_4 i.age_group i.sex i.ethnicity i.imd
global model_5 i.age_group i.sex i.ethnicity i.imd i.bmi ///i.smoking

foreach variable in age_group bmi {
    rename `variable' `variable'_temp
    encode `variable'_temp, generate(`variable')
    drop `variable'_temp
}

rename sex sex_temp
generate sex = 0 if sex_temp == "M"
recode sex . = 1
label define sex 0 "M" 1 "F"
lab values sex sex

destring ethnicity imd, replace
replace imd = 9 if imd == 0

tempname logistic_table
postfile `logistic_table' str20(model) str20(category) or stde ll ul ///
     using $projectdir/output/model_summary, replace


foreach model in model_1 model_2 model_3 {
    foreach exposure of local exposures {

        logistic long_covid i.`exposure' $`model'

        matrix b = r(table)

        qui tab `exposure'
        local unique_values = r(r)

        forvalues n = 2/`unique_values' {
            local category : word `n' of `: colnames b'
            local or = b[1,`n']
            local stde = b[2,`n']
            local lc = b[5,`n']
            local uc = b[6,`n']
            post `logistic_table' ("`model'") ("`category'") (`or') (`stde') (`lc') (`uc')
        }
    }
}
postclose `logistic_table'

* Change postfiles to csv
use $projectdir/output/model_summary, replace

export delimited using $projectdir/output/model_summary$population.csv, replace
