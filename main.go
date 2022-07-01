package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

const  APIKEY = "<YOUR API KEY>"

func main() {
	url:="https://api.countrystatecity.in/v1/countries"

	client := &http.Client{}
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Add("X-CSCAPI-KEY", APIKEY)
	res, _ := client.Do(req)
	defer res.Body.Close()

	bytes ,err := ioutil.ReadAll(res.Body)
	if err != nil {
		fmt.Println(err.Error())
	}
	fmt.Println(string(bytes))
}
