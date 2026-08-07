(function(global){
  class Timeline {
    constructor(options={}) { this._paused=options.paused!==false; this._time=0; this._duration=0; this._tweens=[]; }
    to(target,vars={},position=0) { const start=Number(position)||0,duration=Number(vars.duration)||0; this._tweens.push({target,vars,start,duration}); this._duration=Math.max(this._duration,start+duration); return this; }
    seek(value) { this._time=Math.max(0,Math.min(Number(value)||0,this._duration)); for(const tween of this._tweens){const progress=Math.max(0,Math.min(1,(this._time-tween.start)/(tween.duration||1))); for(const [key,end] of Object.entries(tween.vars)){if(['duration','ease','onUpdate'].includes(key))continue; if(typeof end==='number')tween.target[key]=end*progress;} if(typeof tween.vars.onUpdate==='function')tween.vars.onUpdate();} return this; }
    pause(value) { this._paused=true; if(value!==undefined)this.seek(value); return this; }
    play() { this._paused=false; return this; }
    paused() { return this._paused; }
    time(value) { return value===undefined?this._time:this.seek(value); }
    duration() { return this._duration; }
    totalDuration() { return this._duration; }
    progress(value) { return value===undefined?this._time/this._duration:this.seek(value*this._duration); }
  }
  global.gsap={timeline:(options)=>new Timeline(options)};
})(window);
