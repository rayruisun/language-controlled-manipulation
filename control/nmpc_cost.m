function J = nmpc_cost_horizon(u, q0, robot, eeName, p_ref_h, Q, R, dt)

nq = numel(q0);
Nh = size(p_ref_h,2);

q = q0;
J = 0;

for i = 1:Nh

    ui = u((i-1)*nq+1 : i*nq);

    % State propagation
    q = q + dt * ui;

    % Forward kinematics
    Ti = getTransform(robot, q, eeName);
    pi = Ti(1:3,4);

    % Tracking error
    ei = pi - p_ref_h(:,i);

    % Stage cost
    J = J + ei.' * Q * ei + ui.' * R * ui;

    % Terminal emphasis
    if i == Nh
        J = J + 5 * (ei.' * Q * ei);
    end
end
end

