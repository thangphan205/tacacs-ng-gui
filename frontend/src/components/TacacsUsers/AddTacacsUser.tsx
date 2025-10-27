import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaPlus } from "react-icons/fa"

import { TacacsGroupsService, type TacacsUserCreate, TacacsUsersService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddTacacsUser = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isValid, isSubmitting },
  } = useForm<TacacsUserCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      description: "",
    },
  })

  function getTacacsGroupsQueryOptions() {
    return {
      queryFn: () =>
        TacacsGroupsService.readTacacsGroups(),
      queryKey: ["tacacs_groups",],
    }
  }
  const { data: data_groups } = useQuery({
    ...getTacacsGroupsQueryOptions(),
  })
  console.log(data_groups);
  const mutation = useMutation({
    mutationFn: (data: TacacsUserCreate) =>
      TacacsUsersService.createTacacsUser({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("TacacsUser created successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tacacs_users"] })
    },
  })

  const onSubmit: SubmitHandler<TacacsUserCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-item" my={4}>
          <FaPlus fontSize="16px" />
          Add TacacsUser
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Add TacacsUser</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Fill in the details to add a new item.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.username}
                errorText={errors.username?.message}
                label="Username"
              >
                <Input
                  {...register("username", {
                    required: "username is required.",
                  })}
                  placeholder="username"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.password_type}
                errorText={errors.password_type?.message}
                label="password_type"
              >
                <Input
                  {...register("password_type", {
                    required: "password_type is required.",
                  })}
                  placeholder="password_type"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.password}
                errorText={errors.password?.message}
                label="password"
              >
                <Input
                  {...register("password", {
                    required: "password is required.",
                  })}
                  placeholder="password"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.member}
                errorText={errors.member?.message}
                label="member"
              >
                <Input
                  {...register("member", {
                    required: "member is required.",
                  })}
                  placeholder="member"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <DialogActionTrigger asChild>
              <Button
                variant="subtle"
                colorPalette="gray"
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </DialogActionTrigger>
            <Button
              variant="solid"
              type="submit"
              disabled={!isValid}
              loading={isSubmitting}
            >
              Save
            </Button>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default AddTacacsUser
