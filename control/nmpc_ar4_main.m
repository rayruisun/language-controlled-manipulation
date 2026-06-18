clear; clc; close all;

%% ================= Robot & Initial State =================
robot = importrobot('E:\files\independent_study\ar4_matlab.urdf','urdf');
robot.DataFormat = 'column';
robot.Gravity = [0 0 -9.81];

load('q0_ar4.mat');        % q0
qk = q0;

eeName = 'ee_link';
nq = numel(q0);

%% ================= MPC Parameters =================
dt   = 0.05;               % sampling time
N    = 15;                 % prediction horizon
Tsim = 8;                  % total simulation time
Nt   = round(Tsim/dt);

Q = 80 * eye(3);           % task-space tracking weight
R = 1e-3 * eye(nq);        % joint velocity regularization

%% ================= Joint Limits =================
q_min  = [-2.967; -0.733; -1.553; -pi; -1.833; -pi];
q_max  = [ 2.967;  1.571;  0.908;  pi;  1.833;  pi];
dq_max = 1.0472 * ones(nq,1);

%% ================= Reference Trajectory =================
t = (0:Nt-1) * dt;

p_ref = zeros(Nt,3);
for k = 1:Nt
    p_ref(k,1) = 0.1 * sin(0.24*pi*t(k));
    p_ref(k,2) = 0.1 * sin(0.12*pi*t(k)) - 0.6;
    p_ref(k,3) = 0.47;   % constant height
end

%% ================= Logging =================
q_hist = zeros(Nt,nq);
u_hist = zeros(Nt,nq);
p_hist = zeros(Nt,3);

%% ================= Initial FK =================
T0 = getTransform(robot,qk,eeName);
p0 = T0(1:3,4).';

%% ================= Initial Guess =================
u_opt = zeros(N*nq,1);   % warm start container

%% ================= NMPC Loop =================
for k = 1:Nt

    % Log current state
    q_hist(k,:) = qk.';
    Tk = getTransform(robot,qk,eeName);
    p_hist(k,:) = Tk(1:3,4).';

    % Horizon reference
    idx_end = min(k+N-1, Nt);
    p_ref_h = p_ref(k:idx_end,:).';   % 3 x Nh

    Nh = size(p_ref_h,2);

    % Initial guess (warm start)
    if k > 1
        u_opt = [u_opt(nq+1:end); zeros(nq,1)];
    end
    u0 = u_opt(1:Nh*nq);

    % Bounds
    lb = -repmat(dq_max, Nh, 1);
    ub =  repmat(dq_max, Nh, 1);

    % Cost function
    costfun = @(u) nmpc_cost_horizon( ...
        u, qk, robot, eeName, p_ref_h, Q, R, dt);

    options = optimoptions('fmincon', ...
        'Algorithm','sqp', ...
        'Display','none', ...
        'MaxIterations', 60);

    % Solve NMPC
    u_opt = fmincon(costfun, u0, [], [], [], [], lb, ub, [], options);

    % Apply first control
    u_applied = u_opt(1:nq);
    u_hist(k,:) = u_applied.';

    % State update
    qk = qk + dt * u_applied;

    % Safety: clip joint limits
    qk = min(max(qk, q_min), q_max);
end

%% ================= Plot: Trajectory =================
figure;
plot3(p_ref(:,1), p_ref(:,2), p_ref(:,3), ...
      'k--','LineWidth',1.5); hold on;
plot3(p_hist(:,1), p_hist(:,2), p_hist(:,3), ...
      'r','LineWidth',2);
grid on; axis equal;
xlabel('x'); ylabel('y'); zlabel('z');
legend('Reference','NMPC Tracking');
title('End-effector Trajectory Tracking (Horizon NMPC)');

%% ================= Optional: XY Projection =================
figure;
plot(p_ref(:,1), p_ref(:,2), 'k--','LineWidth',1.5); hold on;
plot(p_hist(:,1),p_hist(:,2),'r','LineWidth',2);
axis equal; grid on;
xlabel('x'); ylabel('y');
legend('Reference','Tracking');
title('XY-plane Trajectory');
