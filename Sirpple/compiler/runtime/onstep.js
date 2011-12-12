onStep = function(dt)
{
    dt += onStep_leftover;
    while(dt > 30)
    {
        {{target}}.dispatchEvent(onStepEvent);
        dt -= 30;
    }
    onStep_leftover = dt;
};
