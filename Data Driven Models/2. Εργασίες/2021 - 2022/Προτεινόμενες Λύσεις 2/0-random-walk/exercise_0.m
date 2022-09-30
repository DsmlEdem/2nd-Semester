function [means, vars, mean_muX, var_muX] = exercise_0(n_steps, n_samples)
    
    n_steps = n_steps + 1;  % Including the initial position (0-th step)
    
    % X(t_n) of each sample.
    pos = zeros(n_samples, 1);  % Initial positions
    % E[X(t_n)] of each time step n. True value is 0 for all n.
    means = zeros(n_steps, 1);
    means(1) = mean(pos);
    % V[X(t_n)] of each time step n. True value is n.
    vars = zeros(n_steps, 1);
    vars(1) = var(pos);
    % Average over all time (for each sample). Random variable muX.
    muX = pos;
    
    for i = 2:n_steps
        step = 2 * (rand(n_samples, 1) > 0.5) - 1;  % random +-1s
        pos = pos + step;
        means(i) = mean(pos);
        vars(i) = var(pos);
        muX = muX + (pos - muX) / i;  % running update
    end
    % Expected value of average over all time. True value is 0.
    mean_muX = mean(muX);
    % Variance of average over all time.
    % True value is 1/6 * (n_steps + 1) / n_steps * (2*n_steps + 1) 
    var_muX = var(muX);
end