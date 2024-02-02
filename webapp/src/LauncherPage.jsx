import React from "react";
import { useForm } from "react-hook-form";

const LauncherPage = ({ onLaunch }) => {
  const { register, handleSubmit } = useForm();

  return (
    <div>
      <form onSubmit={handleSubmit(onLaunch)}>
        <input defaultValue="" {...register("channelName")} placeholder="Channel" />
        <input defaultValue="" {...register("userName")} placeholder="Username" />
        <input type="submit" value="Join" />
      </form>
    </div>
  );
};

export default LauncherPage;
