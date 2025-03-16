# IM Results

Code to extract results from RTRT.me along with the results themselves in three formats:

- JSON: The original data as extracted. Nothing has been done to cleanse or transform this. If it comes from an endpoint that does pagination the data will still be in pages.
- CSV: 
    - Tall: The points are arranged in rows and include all splits available. Times are available both in HH:MM:SS and total seconds. There are mulitple rows per athelete. Leg and finish positions are included. This is likely the best option for further analysis.
    - Wide: The points are arranged in rows and only include Swim End, Bike End and Run End/Finish. Athletes who take the start but do not complete the swim are omitted. Only finish positions are included.
    - Both Tall & Wide: Rank is effectively an overall position of *everyone* (Pro, Age Group, Relay, Open, Physically Challenged). It is primarily just used to sort the results. Leg and finish positions are recalculated based on times but should match with those present on the tracker. They are given within the division type as they are on the tracker.
    - Events: This is a list of all events for which results are potentially available.

As these results are from the tracker they may differ from the official results (but most likely not).

## Result Requests

If you would like results for a particular event raise an issue for it and I will extract it when I get time to. You can do so yourself if you can workout how to obtain the `app_id` needed to authenticate.

I intend to work my way through the 2025 events but may not go backwards to past years.

## License

The code contained within this repository is licensed under the MIT License.

Data likely remains the property of its owner. Personal use is probably acceptable but anything else is possibly problematic.
