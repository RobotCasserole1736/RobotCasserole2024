/////////////////////////////////////////////////////////////////////////
// Signal - A set of samples with monotomically-increasing time.
/////////////////////////////////////////////////////////////////////////

export class Signal {

    constructor(name_in, units_in) { 
        this.name = name_in;
        this.units = units_in;
        this.sampleList = []; //Assumed to be entered in monotomically-increasing order
        this.latestSampleTime = 0;
        this.firstSampleTime = 0;
    }

    //Add a new sample to the signal 
    // Based on NT4 requirements, to not assume samples are added monotomically
    addSample(newSample){
        if(this.sampleList.length == 0){
            this.firstSampleTime = newSample.time;
        }
        this.latestSampleTime =  Math.max(newSample.time, this.latestSampleTime);
        
        var insIdx = this.getIndexOfTime(newSample.time)+1;
        this.sampleList.splice(insIdx, 0, newSample);
    }

    //Get all samples in a given time range. Might return empty if no samples present
    getSamples(startTime, endTime){
        var retList = [];
        var startIdx = this.getIndexOfTime(startTime);
        var endIdx = this.getIndexOfTime(endTime);


        if(startIdx != null && endIdx != null){
            for(var idx = startIdx; idx < endIdx; idx++){
                retList.push(this.sampleList[idx]);
            }    
        }

        return retList;
    }

    //Return the first sample at or after the given time.
    //Might return null if no sample is after given time.
    getSample(time_in){
        var retSample = null;
        var idx = this.getIndexOfTime(time_in);
        if(idx != null){
            retSample = this.sampleList[idx];
        }
        return retSample;
    }

    //Clear out all samples
    clearValues(){
        this.sampleList = [];
    }

    //Return the most-recently-added sample
    //Might return null if no sample has been added yet.
    getLatestSample(){
        if(this.sampleList.length > 0){
            return this.sampleList[this.sampleList.length-1];
        } else {
            return null;
        }
    }

    //Optimized timeseries arbitrary lookup
    // Looks horrible. Hopefully works better than linear search.
    getIndexOfTime(time_in){
        var len = this.sampleList.length;

        if(len == 0){
            return null; // no samples. Return null
        } else if (len == 1) {
            return 0; // only one sample, return it.
        } else if(time_in <= this.firstSampleTime){
            return 0; //User asks for sample before known time. Return first sample
        } else if(time_in >= this.latestSampleTime){
            return len-1; //User asks for a future asmple. Return the latest.
        } else {
      
            //Main algorithm - assume the points are roughly equally spaced and start guessing about where
            // we'd expect the requested point to be.
            var signalTimeSpan = this.latestSampleTime - this.firstSampleTime;
            if(signalTimeSpan > 0){
                var guessIdx = Math.floor( (this.sampleList.length-1) * (time_in-this.firstSampleTime) / (signalTimeSpan));

                while(true){ //return statements expected to kick out out of this loop.
                    var guessTime = this.sampleList[guessIdx].time;

                    if(guessTime > time_in){
                        //Guessed too high, look backward in list
                        if(guessIdx <= 0){
                            return 0; // nowhere to look backwrd, just return first element
                        } else {
                            var guessTimeNext = this.sampleList[guessIdx-1].time;
                            if(guessTimeNext < time_in){
                                //We found the right interval, return the upper bound.
                                return guessIdx;
                            } else {
                                //Not in this interval, keep going.
                                guessIdx = guessIdx - 1;
                                continue;
                            }
                        }


                    } else if (guessTime < time_in){
                        //Guessed too low, move forward in list
                        if(guessIdx >= len-1){
                            return len-1;//Nowhere to move forward, just return last element
                        } else {
                            var guessTimeNext = this.sampleList[guessIdx+1].time;
                            if(guessTimeNext > time_in){
                                //We found the right interval, return the upper bound.
                                return guessIdx + 1;
                            } else {
                                //Not in this interval, keep going.
                                guessIdx = guessIdx + 1;
                                continue;
                            }
                        }

                    } else {
                        //hot dog got it spot on!
                        return guessIdx;
                    }
                }


            } else {
                return len-1; //Edge case - samples provided are all on the same timestamp - just return the most recently submitted one
            }


        }


    }

}