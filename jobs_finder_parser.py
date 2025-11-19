import requests
from bs4 import BeautifulSoup
import re
import json
import time
from langchain_community.llms import Ollama
#python3.12 + old libs
#gpt-oss good, llama3.1:8b - good,gemma3:4b-it-qat
ollama = Ollama(
    model="gemma3:4b-it-qat"

)  # assuming you have Ollama installed and have llama3 model pulled with `ollama pull llama3 `

timestr = time.strftime("%Y%m%d-%H%M%S")

filelog = open(f'jobsearch_log{timestr}.txt', 'w')
result = open(f'jobsearch_result{timestr}.txt', 'w')
verification_jobs = open('double_verification.txt', 'w')

job_ids = []


def hundred_range(n):
    start = 0  # start at 0
    while start < n:  # continue until we reach the input number
        yield start  # yield the current value
        start += 100  # increment by 100 to get the next multiple of 100


def requester(url):
    headers = {
        'Cookie': f'li_at={session_cookie};' f'JSESSIONID="ajax:{cssrftoken}";',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Csrf-Token': f'ajax:{cssrftoken}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def get_jobs_search(keywords, timer, jobtype, geoId):
    if jobtype == "remote":
        url = f'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-207&count=100&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:{keywords},locationUnion:(geoId:{geoId}),selectedFilters:(timePostedRange:List(r{timer}),workplaceType:List(2)),spellCorrectionEnabled:true)&start=0'
    elif jobtype == "onsite":
        url = f'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-207&count=100&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:{keywords},locationUnion:(geoId:{geoId}),selectedFilters:(distance:List(25),timePostedRange:List(r{timer}),workplaceType:List(1,3)),spellCorrectionEnabled:true)&start=0'

    # print(url)

    description_json = json.loads(requester(url).decode_contents(json), strict=False)
    # print(description_json)
    results_quantity = json.dumps(description_json["metadata"]["subtitle"]["text"], indent=4)
    digit = re.compile('\d+')
    digitre = digit.findall(results_quantity)
    digital = int(digitre[0])
    print(digital)
    print(results_quantity, file=filelog)
    if digital == 0:
        print("Value is zero. Stopping function execution.")
        return
    elif digital > 100:
        for i in hundred_range(digital):
            if jobtype == "remote":
                url = f'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-207&count=100&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:{keywords},locationUnion:(geoId:{geoId}),selectedFilters:(timePostedRange:List(r{timer}),workplaceType:List(2)),spellCorrectionEnabled:true)&start={i}'
            if jobtype == "onsite":
                url = f'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-207&count=100&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_JOB_FILTER,keywords:{keywords},locationUnion:(geoId:{geoId}),selectedFilters:(timePostedRange:List(r{timer}),workplaceType:List(1,3)),spellCorrectionEnabled:true)&start={i}'
            bobo = requester(url)
            description_json = json.loads(str(bobo.text))
            jobsids = json.dumps(
                description_json["metadata"]["jobCardPrefetchQueries"][0]["prefetchJobPostingCardUrns"],
                indent=4)
            regex = re.compile('urn:li:fsd_jobPostingCard:\((\d+)')
            regex_jbid = regex.findall(jobsids)


            for result in regex_jbid:

                if result not in job_ids:
                    job_ids.append(result)

            print(job_ids, file=filelog)

    elif digital <= 100:
        jobsids = json.dumps(description_json["metadata"]["jobCardPrefetchQueries"][0]["prefetchJobPostingCardUrns"],
                             indent=4)
        regex = re.compile('urn:li:fsd_jobPostingCard:\((\d+)')
        regex_jbid = regex.findall(jobsids)

        for result in regex_jbid:
            if result not in job_ids:
                job_ids.append(result)
        print(job_ids, file=filelog)


final_jobs = []
double_verification_jobs = []


def get_job_descriptiontext(jobid):
    print('number is ' + jobid)
    url = f'https://www.linkedin.com/voyager/api/graphql?variables=(cardSectionTypes:List(JOB_DESCRIPTION_CARD),jobPostingUrn:urn%3Ali%3Afsd_jobPosting%3A{str(jobid)},includeSecondaryActionsV2:true)&queryId=voyagerJobsDashJobPostingDetailSections.9ab5a43d0466e1d5649150f6b39575de'

    try:
        description_json = json.loads(requester(url).decode_contents(json), strict=False)
    except:
        print(jobid + "   Id is getting error!!!")
        return
    try:
        date = json.dumps(description_json["data"]["jobsDashJobPostingDetailSectionsByCardSectionTypes"]["elements"][0][
                              "jobPostingDetailSection"][0]["jobDescription"]["postedOnText"], indent=4)
    except:
        print(jobid + "  date getting error !!!")
        pass

    try:
        text = json.dumps(description_json["data"]["jobsDashJobPostingDetailSectionsByCardSectionTypes"]["elements"][0][
                              "jobPostingDetailSection"][0]["jobDescription"]["jobPosting"]["description"]["text"],
                          indent=4)
    except:
        print(jobid + "  text getting error !!!")
        return


    # this one is relevant for mistral
    # get_description = ollama.invoke(f"Is this one relevant for social media marketing specialist or social media marketing manager. Be precise and analyze the text deeply, but without clarification. Give me an answer with 1 word Yes or No. {text}")
    get_description = ollama.invoke(
        f"Is this one relevant for social media marketing specialist or social media marketing manager. Be precise and analyze the text deeply, but provide me a short answer Yes or No, without clarification. Say No if position is for senior specialist in title or requires more than 3 years of experience and specifically mentions years of experience. Also say no for SEM jobs. {text}")
    '''get_description = ollama.invoke(
        f"Is this one relevant for penetration tester?. But be precise and analyze the text deeply. If clearence is needed say No or if it is more like a defensive position related to administering systems not attacking also say No. If Forensics, DFIR, XDR, Architect say No and for incident response say No. Provide me a short answer Yes or No, without clarification. {text}")'''
    # this one is relevant for llama3
    # get_description = ollama.invoke(f"Is this one relevant for social media marketing specialist or social media marketing manager. Be precise and analyze the text deeply, but provide me a short answer Yes or No, withiout clarification. {text}")
    print(date, file=filelog)
    print(text, file=filelog)
    print(get_description, file=filelog)
    print(get_description)
    if "Yes" in get_description or "YES" in get_description:
        print(jobid, file=filelog)
        print('=================================\n', file=filelog)
        final_jobs.append(jobid)
    elif "No" in get_description or "NO" in get_description:
        print("Not suitable", file=filelog)
        print('=================================\n', file=filelog)
        double_verification_jobs.append(jobid)
    else:
        print(jobid + '  Error occured!')


def get_job_url(jobid):
    url = f'https://www.linkedin.com/voyager/api/jobs/jobPostings/{jobid}?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65&topN=1&topNRequestedFlavors=List(TOP_APPLICANT,IN_NETWORK,COMPANY_RECRUIT,SCHOOL_RECRUIT,HIDDEN_GEM,ACTIVELY_HIRING_COMPANY)'

    description_json = json.loads(requester(url).decode_contents(json))
    position_level = json.dumps(description_json["formattedExperienceLevel"], indent=4)
    position_title = json.dumps(description_json["title"], indent=4)

    applymethod = json.dumps(description_json["applyMethod"], indent=4)
    company = json.dumps(description_json["companyDetails"], indent=4)
    company_linkedin = json.dumps(description_json["companyDetails"], indent=4)
    # print(company_linkedin)

    print("\n==================================================\n", file=result)
    print(position_title, file=result)
    print(position_level, file=result)

    print("\n==================================================\n")
    print(position_title)
    print(position_level)

    try:
        if 'companyName' in company:
            company_linkedin = json.dumps(
                description_json["companyDetails"]["com.linkedin.voyager.jobs.JobPostingCompanyName"]["companyName"],
                indent=4)
            print(company_linkedin, file=result)
            print(company_linkedin)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}', file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}')

        else:
            company_linkedin = json.dumps(
                description_json["companyDetails"]["com.linkedin.voyager.deco.jobs.web.shared.WebJobPostingCompany"][
                    "companyResolutionResult"]["url"], indent=4)
            print(company_linkedin, file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}', file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}')

        if 'easyApplyUrl' in applymethod:
            print('Easy Apply', file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}', file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}')
        elif 'SimpleOnsiteApply' in applymethod:
            print('Easy Apply', file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}', file=result)
            print('Linkedin: ' + f'https://www.linkedin.com/jobs/search/?currentJobId={jobid}')
        else:
            company_apply_url = json.dumps(
                description_json["applyMethod"]["com.linkedin.voyager.jobs.OffsiteApply"]["companyApplyUrl"], indent=4)
            print(company_apply_url, file=result)
            print(company_apply_url)

    except:
        Exception
        print('Recheck the ID ' + f'{jobid}')
        print('Recheck the ID ' + f'{jobid}', file=result)



if __name__ == "__main__":
    session_cookie = ''  # Replace with your LinkedIn session cookie 'li_at='
    cssrftoken = 'justnumber' # Jsessionid after 'ajax:TOKEN'

    choice = 'marketing'
    #choice = 'cybersecurity'
    if choice == 'marketing':
        keywords = ['social+media+manager', 'marketing%20project%20manager', 'content+creator', 'marketing+assistant',
                    'community+manager', 'account+coordinator', 'marketing+coordinator', 'marketing+events+specialist',
                    'advertising', 'account+executive']
    elif choice == 'cybersecurity':
        keywords = ['senior+application+security+engineer', 'senior+penetration+tester',
                    'senior+cybersecurity+engineer', 'senior+cybersecurity+consultant',
                    'senior+application+security+consultant', 'penetration+tester']

    # TIME for search
    oneweek = '604800'
    oneday = '86400'
    timer = oneweek
    #jobtype = "remote"
    jobtype = "onsite"
    geoId = "106383538" #go to jobs section on linkedin and search for your job and city, right after the search, look for geoId in url bar, this is the geoId for your city

    for keyword in keywords:
        get_jobs_search(keyword, timer, jobtype, geoId)

    print(' Found Jobs = ' + str(len(job_ids)) + '\n' + '===============')
    print(' Found Jobs = ' + str(len(job_ids)) + '\n' + '===============', file=filelog)
    s = '\n'.join(str(x) for x in job_ids)
    for jid in job_ids:
        '\n'.join(str(jid))
        get_job_descriptiontext(jid)

    print(final_jobs, file=filelog)

    print(len(final_jobs), file=result)
    for final in final_jobs:
        '\n'.join(str(final))
        get_job_url(final)

    print(double_verification_jobs, file=verification_jobs)
    verification_jobs.close()
    filelog.close()
    result.close()
